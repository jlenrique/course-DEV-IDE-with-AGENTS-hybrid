# Codex dispatch: Third-pass verification-only re-trace on Slab 6.4 cycle 2 remediation

**Session:** 2026-04-28 (operator-authorized post-cycle-2-commit)
**Branch:** `dev/langchain-langgraph-foundation`
**Predecessor state:**
- Cycle 1 remediation `c2df610` → second-pass full review HALT (3 re-trace FAILs) → operator-ratified URL-pattern fallback (Rust-regex no-lookahead) → cycle 2 remediation `1151bdc`
- Codex-side cycle 2 verification: 1 + 9 + 63 + 83 + 82 passed (all relevant slices); ruff PASS; sandbox-AC PASS
- No decision_needed items surfaced from cycle 2
- Story status: `migration-6-4-irene-pass-2-authoring-template: review` (correctly held; not yet flipped to done)

**Mission:** verification-only re-trace by Acceptance Auditor on the 3 cycle-2 patches. Tight scope: confirm each cycle-2 patch addressed its second-pass finding correctly + no regression in cycle 1 or earlier work + no NEW patches surface.

**Operator preference (binding):** "do it right, no band-aids, only rational trade-offs that get named in writing." Aggressive DISMISS for cosmetic NITs.

## Disposition rules

- **`re-trace PASS`:** cycle-2 patch addressed second-pass finding correctly
- **`re-trace FAIL`:** cycle-2 patch did NOT address correctly; auto-promote to NEW patch (cycle 3 needed)
- **NEW patch:** new defect surfaced beyond the 3 cycle-2 patches; HALT and surface
- **NEW decision_needed:** beyond the 3 ratified DN dispositions (6.3-DN-1/2 + 6.5-DN-1) + cycle-2 URL-pattern fallback; HALT and surface

## Per-finding re-trace targets

### 6.4-SP2-BH-1 re-trace (JSON Schema rejects remote .png URLs)

**Verify:**
- `LOCAL_PNG_PATH_PATTERN` at `app/specialists/irene/authoring/pass_2_template.py:10` matches the operator-ratified pattern: `^(?:[A-Za-z]:[\\/])?[^:]+[.][Pp][Nn][Gg]$`
- Trade-off comment present in code per dispatch instruction (documents Rust-regex constraint + over-restriction trade-off + operator-ratification date 2026-04-28)
- Pattern applied via `Field(..., pattern=LOCAL_PNG_PATH_PATTERN)` for: `gary_slide_output.file_path`, `perception_artifacts.source_image_path`, `segment_manifest.visual_file`
- Pydantic field validators at `:61, :67` STILL in place (defense-in-depth preserved; not removed in cycle 2)
- New test `test_json_schema_rejects_remote_png_urls` (or equivalent) exists; covers all 4 URL schemes (http, https, file, ftp) × all 3 fields = ≥12 assertions
- New test passes; produces non-zero count (not silent skip)
- Run: `.venv/Scripts/python.exe -m pytest tests/unit/specialists/irene/test_pass_2_template_strict.py -k "json_schema_rejects_remote" -q --tb=short` → expect 1 PASS

### 6.4-SP2-EH-1 re-trace (validator-oracle alignment full)

**Verify:**
- Test at `tests/integration/specialists/irene/test_pass_2_template_validator_alignment.py` enumerates all 39 `errors.append(...)` + 11 `warnings.append(...)` = 50 enforcement points from `validate-irene-pass2-handoff.py`
- Each enumerated entry has explicit `expected_coverage: Literal["schema", "procedural", "skipped"]` + non-empty `rationale` field
- Skipped entries have rationale that explains skip (e.g., warning-only; covered by docs; etc.) — not "TODO" or empty
- Drift-guard meta-test exists: counts `errors.append(...)` + `warnings.append(...)` sites in validator file; asserts equals enumeration length
- Drift-guard meta-test passes (validator counts match enumeration)
- Run: `.venv/Scripts/python.exe -m pytest tests/integration/specialists/irene/test_pass_2_template_validator_alignment.py -q --tb=short` → expect 63 PASS per Codex report
- Verify Codex chose Approach B (explicit enumeration) per recommended default; if Approach A (validator refactor) was used, verify validator's `RULES` constant export is consistent + tested

### 6.4-SP2-AA-1 re-trace (ProceduralRule closed-enum 3-surface)

**Verify:**
- `ProceduralRule` enum added to closed-enum 3-surface red-rejection parametrize at `tests/unit/specialists/irene/test_pass_2_template_strict.py:103` (or equivalent updated location)
- All 8 enums (schema_version, composition_mode, visual_detail_load, content_density, bridge_type, cluster_role, cluster_position, **procedural_rules**) get uniform 3-surface treatment:
  1. Pydantic `Literal` red-rejection (instantiation with unknown value raises `ValidationError`)
  2. JSON Schema `enum` red-rejection (`jsonschema.validate(...)` rejects unknown value)
  3. Explicit shape-pin (assertion that unknown value is NOT in accepted list)
- New `procedural_rules` unknown-value test passes
- Run: `.venv/Scripts/python.exe -m pytest tests/unit/specialists/irene/test_pass_2_template_strict.py -k "closed_enum or procedural_rule" -q --tb=short` → expect 9 PASS per Codex report

## Cycle 1 + earlier work non-regression verification

Run focused Irene unit + integration suite + composition smoke:
```bash
.venv/Scripts/python.exe -m pytest tests/unit/specialists/irene/ tests/integration/specialists/irene/ tests/composition/test_irene_pass_2_template_composition_smoke.py -q --tb=short
```
Expected: ~82-83 passed per Codex report; no regressions vs cycle 1 baseline.

## Per-rider re-trace summary

| Cycle-1 BINDING rider | Cycle-2 status |
|---|---|
| W-R1 (Pydantic authoritative) | Re-verify still satisfied; JSON Schema mirroring complete via new pattern |
| W-R2 (Markdown-Pydantic alignment test) | Re-verify alignment test still passes; cycle 2 didn't touch |
| W-R3 (unidirectional schema-first validation) | Re-verify still documented; cycle 2 didn't touch |
| M-R1 (procedural rules enumeration) | Re-verify still satisfied; expanded by cycle 2 to enumerate all 50 validator sites |
| M-R2 (schema-valid procedural-reject test) | Re-verify still passes; cycle 2 didn't touch |
| M-R3 (validator oracle alignment full) | **Now FULLY satisfied per cycle 2 (50 enumerated)** |
| P-R1 (3 worked examples from B-Run §08) | Re-verify still in template; cycle 2 didn't touch |
| P-R2 (bidirectional cross-link) | Re-verify still satisfied; cycle 2 didn't touch |
| A-R1 (Phase 1 act-body-category pre-flight) | Pre-flight passed cycle 1; cycle 2 didn't touch _act |
| A-R2 (cluster-arc decision_needed escalation) | Cycle 2 didn't surface; Mary harvest-gate evaluates A18 at close |
| QR-R1 (composition smoke) | Re-verify still passes |
| QR-R2 (N4 + N11 PASS verification) | Re-verify N4 + N11 still PASS |

## N-item re-trace summary

| N-item | Cycle-1 second-pass verdict | Cycle-2 re-trace target |
|---|---|---|
| N4 — isolation invariant preserved | PASS | Re-verify PASS |
| N5 — cross-component state-flow contract | FAIL (Markdown contradictions; JSON Schema weaker) | **Re-verify now PASS** (Markdown contradictions purged cycle 1; JSON Schema URL-rejection cycle 2) |
| N7 — replay regression | PASS | Re-verify PASS |
| N9 — operator-witnessed evidence | PASS-PENDING-OPERATOR (Gate 5 still pending) | Re-verify PASS-PENDING-OPERATOR |
| N11 — composition mode declared | PASS | Re-verify PASS |

N1, N2, N3, N6, N8, N10, N12 remain N/A.

## Required deliverable section

Triaged third-pass review record at `_bmad-output/implementation-artifacts/6-4-third-pass-verification-2026-04-28.md` with:

- **Per-finding re-trace verdict** for the 3 cycle-2 patches (PASS / FAIL)
- **Per-rider re-trace summary** (12-row table per the matrix above)
- **N-item re-trace summary** (verdicts updated post-cycle-2)
- **Mary harvest-gate A18 candidate evidence** (per MA-R2 NON-BLOCKING) — enumerate which validator rules went schema vs procedural with rationale per rule (this becomes operator + Mary's evidence base for A18 disposition at close)
- **Final sentence:** "Story 6.4: third-pass re-trace verifies all 3 cycle-2 patches addressed correctly; cycle 1 + earlier rider re-trace clean; N-item trace shows N5 PASS (was FAIL); Mary harvest-gate A18 evidence captured. Story 6.4 ready for Gate 5 operator-side dual-gate evidence ceremony, then `review → done` flip per discipline doc Gate 6."

OR (if any FAIL or NEW patch surfaces): "Story 6.4: re-trace surfaced X FAIL / Y NEW patch; cycle 3 needed."

## Halt-and-surface triggers

HALT if:
- Re-trace FAIL on any of the 3 cycle-2 patches (means cycle 2 didn't address correctly; cycle 3 needed)
- NEW patch surfaces beyond the 3 cycle-2 patches (means cycle 2 introduced regression OR original second-pass missed something)
- NEW decision_needed item surfaces beyond ratified dispositions
- Cycle 1 BINDING rider re-trace shows regression (cycle 2 broke something cycle 1 satisfied)
- N-item FAIL on any previously-PASS N-item (cycle 2 broke something)
- Substrate disagreement (out-of-scope file modified)
- Composition Spec §11 migration trigger fires

## What this dispatch does NOT do

- Does NOT touch any code (verification-only)
- Does NOT flip 6.4 to done (operator runs Gate 5 dual-gate + close protocol after this clears)
- Does NOT replace operator's Gate 5 dual-gate evidence ceremony
- Does NOT modify anti-pattern catalog (Mary harvest-gate evaluates A18 at close based on this re-trace's evidence collection)
- Does NOT re-litigate operator-ratified party-mode BINDING riders, DN dispositions, or URL-pattern fallback
- Does NOT trigger first tracked trial

## Closeout posture

When third-pass clears:
1. Codex final report: PASS verdicts per cycle-2 patch; per-rider re-trace summary; N-item summary; Mary harvest-gate A18 evidence
2. **Operator runs Gate 5 dual-gate live evidence ceremony** per spec — exercises Pass 2 authoring template end-to-end on a real (or representative) Pass 2 corpus; pastes evidence into Dev Agent Record §"Operator dual-gate gate-2 evidence"
3. **Mary harvest-gate A18 disposition** — operator + Mary review the validator-rules-enumeration evidence (schema vs procedural per rule); decide:
   - File A18 ("State-machine modeling rescues seemingly-procedural validation") in `docs/dev-guide/specialist-anti-patterns.md` Post-Cycle Harvest section IF cycle 2 work surfaced clean state-machine pattern, OR
   - Leave A18 as candidate (Codex's current disposition); revisit at next state-machine-shaped substrate work
4. **Formal 6.4 close** per discipline doc Gate 6: sprint-status flip review → done with full lineage citation; deferred-inventory `Last refreshed:` line update; Composition Spec §10 N/A (no substrate change; Irene `_act` body category unchanged)
5. **First tracked trial UNBLOCKED** — bundle 3/3 closed; substrate-polish tail of migration complete

Total wall-clock to first-tracked-trial UNBLOCK from this dispatch: ~30-60 min Codex + operator Gate 5 ceremony (~10-30 min) + close edits (~5-10 min). Achievable in this session.
