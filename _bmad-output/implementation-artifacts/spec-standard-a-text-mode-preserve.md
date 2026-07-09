# Spec: Standard-A styleguide text_mode preserve (Fidelity L1 alignment)

**Status:** done  
**Workflow:** `bmad-quick-dev`  
**Party green-light:** 2026-07-09 — Winston/Amelia/John consensus **A**  
**Evidence:** trial `62308889` / `IRENE-FIGURE-CONTRADICTION-TRIAGE.md`

## Goal

Align permanent standard-A guide `hil-2026-apc-crossroads-classic` with Fidelity L1:
`text_mode=preserve` so Gamma cannot drop teaching numerals (10%/90%) that Pass-2
must narrate, which currently fires `irene.pass2.figure-contradiction`.

## Acceptance Criteria

1. **Given** the SSOT record for `hil-2026-apc-crossroads-classic`, **when** loaded,
   **then** `prompt_configuration.text_content.mode == preserve` and `amount` is absent/null.
2. **Given** `resolve_styleguide` / expand for that guide, **when** projected to Gary
   settings, **then** `text_mode == "preserve"`.
3. **Given** `validate_gamma_style_guides.py`, **when** run offline, **then** PASS.
4. Existing `DEFAULT_VARIANT_PAIR` preserve pin remains green.

## Tasks

1. Patch `state/config/gamma-style-guides.yaml` classic record (+ prose/provenance).
2. Add regression test pinning classic → preserve.
3. Update deferred-inventory triage entry; leave S8 CLOSED pending re-proof.
