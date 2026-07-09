# Spec: Gamma title-residue / cover-drop residual bind

**Status:** done  
**Workflow:** `bmad-quick-dev`  
**Party green-light:** 2026-07-09 — Winston B, Amelia A, John A  
**Out of scope:** S8 letter reopen; LLM matcher epic; `_act` filename churn

## Goal

When bijective containment leaves exactly one unmatched brief slot and exactly one unmatched export page (often misclassified as a leading cover), attempt a **cardinality-gated residual soft bind** so morphological rephrases (e.g. Completion↔Complete) bind instead of mute cover-drop + `brief-unmatched`.

## Live pin (trial `bc0f81c4`)

| Side | Title |
| --- | --- |
| Brief `slide-01` | Module 1 Completion and Mindset Closure |
| Page | Module-1-Complete-The-Mindset-is-Set |

Containment fails; page was dropped as cover → `unmatched pages: []`.

## Acceptance Criteria

1. **Given** the live Completion/Complete pair with four other uniquely contained slides, **when** `match_pages_to_slots` runs, **then** `slide-01` binds to that page; `dropped_pages` / `unmatched_keys` / `unmatched_pages` empty for that residue.
2. **Given** cycle-6 F8 corpus (cover + merged summary), **when** matcher runs, **then** cover still drops; `slide-06` stays unmatched (residual must NOT bind cover↔summary).
3. **Given** two unmatched slots or two unmatched pages after bijective, **when** residual would apply, **then** no soft bind; fail-loud surfaces unchanged.
4. **Given** one unmatched slot + one leading unmatched page with weak overlap only, **when** soft gate fails, **then** cover-drop may proceed (F8 path).
5. Bijective containment edges unchanged; residual runs only after the bijective commit.

## Tasks

1. Add `_residual_soft_compatible` (+ stem helpers) in `skills/gamma-api-mastery/scripts/gamma_operations.py`.
2. In `match_pages_to_slots`, after bijective commit and before cover classification: 1:1 residual attempt; on success bind and clear residue; on failure fall through to existing cover-drop.
3. RED→green tests in `tests/specialists/gary/test_gamma_title_matching.py`.
