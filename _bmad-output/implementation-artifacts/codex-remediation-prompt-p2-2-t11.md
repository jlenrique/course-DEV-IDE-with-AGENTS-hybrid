# Codex Remediation Prompt — P2-2 (T11 hand-back, 2026-06-20)

**Story:** `p2-2-perception-artifact-vision-node`
**Branch:** `fidelity-perception-arc-2026-06-19`
**Why you're here:** Claude T11 review + a fully-spawned 3-lane code review + party-mode (5/5) **handed P2-2 back** for a consolidated T1–T10 remediation. Your prior T1–T10 work is **still in the working tree (uncommitted)** — build on it; do not start over. Full evidence: `_bmad-output/implementation-artifacts/p2-2-t11-code-review-2026-06-20.md`. Spec (unchanged ACs + amendments): `spec-p2-2-perception-artifact-vision-node.md`.

This is ONE consolidated cycle. Re-run T11 will FAIL unless every item below is closed. F1 is the long pole — start there.

---

## MUST-FIX

### F1 — Comparator θ/d calibration is VACUOUS (the anchor; party pass-bar is strict)
Files: `app/specialists/vision/repeatability.py`, `tests/specialists/vision/test_vision_repeatability.py`, new fixtures under `tests/fixtures/perception/`.
Current defect: pass-case compares a fixture **to itself** (`compare_artifacts(X, X)` — a tautology); the only negative control trips `element_jaccard_min=1.0` (exact-equality, not a tolerance); `bbox_iou_min=0.90` and `text_edit_distance_max=8.0` are **never exercised at a boundary** (set them to 0.0/10000 and every test still passes). Violates binding amendment M-3/M-4.
**Required (Murat, binding):**
1. **Held-out labeled set, not self-compare.** Pass-case fixtures must be a (reference, candidate) pair that is *known-equivalent-but-not-byte-identical* (re-encoded / re-laid-out), with the fidelity verdict authored independently of the threshold values. `x == x` is banned.
2. **One negative control per threshold**, each tripping ONLY its own knob and staying green on the others:
   - fails ONLY `bbox_iou` (geometry perturbed; elements + text intact),
   - fails ONLY `element_jaccard` (element set diverged; geometry + text intact),
   - fails ONLY `text_edit_distance` (text drifted past the bound; geometry + elements intact).
3. **Per-threshold mutation proof, tabulated in Completion Notes.** For each threshold, set it to its degenerate extreme (0.0 / 10000); the corresponding negative test MUST flip red→green. Paste the table. A threshold no test can make fail is decorative and will fail re-T11.

### MF1 — Core detector `_FIGURE_RE` captures stray trailing letters → false Class-A blocks
File: `app/specialists/quinn_r/fidelity_detector.py:18-19`.
`\$\s*\d+(?:\.\d+)?\s*(?:t|trillion|b|billion)?` has no trailing boundary and allows whitespace before the unit, so `_figures("$5 to enroll")` → `{'money-trillion:5'}` (≡ "$5 trillion"). Add a word-boundary / unit anchor so a bare amount followed by an ordinary word is NOT read as a unit-bearing figure.
**Required:** an adversarial RED-must-not-fire corpus as fixtures — at least `"$5 to enroll"`, `"$4 tax"`, `"$5 there"`, ordinals, version numbers (`v5`), page refs — all green-silent, WHILE a true `"$5 trillion"` / `"$4.5T"` case still normalizes and still fires on a genuine contradiction. Beware regex blast radius: pin before/after on the whole figure-normalization path.

### M3 — `FIDELITY_GATE=warn` swallows STRUCTURAL integrity failures
File: `app/specialists/quinn_r/_act.py:176-192`.
The `except FidelityError` wraps the entire `detect_fidelity` call, so the operator break-glass also downgrades schema-drift / duplicate-artifact / missing-artifact errors (raised with `ORPHAN_TAG` by `_artifact_map`) — not just narration mismatches. AC-17 scoped warn to **narration fidelity only**.
**Required:** scope the warn-downgrade to the narration-fidelity tags (`fidelity-orphan-reference` on actual narration reference checks + `fidelity-figure-contradiction`); structural FidelityErrors (schema validation, duplicate slide, missing artifact) MUST still raise even under `FIDELITY_GATE=warn`. Verify the exception types/tags are separable at the catch site (do not string-sniff the message). Add a test: malformed/duplicate artifact under `FIDELITY_GATE=warn` still raises.

### F2 — 07G breaks `test_33_1a_verbatim_extraction` (party Option A, with the closed guard)
File: `tests/contracts/test_33_1a_verbatim_extraction.py` (+ a new meta-test).
07G is net-new prose; verbatim-extraction from the frozen v4.2 source structurally cannot hold. **Do NOT edit the frozen pack.** Implement Option A as ratified:
1. **Closed allowlist** of net-new / value-substituting sections (extend the existing `_VALUE_SUBSTITUTING_SECTIONS` pattern), each entry carrying: section id + reason (net-new-prose / value-substituting) + the substitute invariant that covers byte-fidelity (for 07G: **L1 Check-9 regeneration-determinism**). Not a regex any future `07X` silently matches.
2. **Meta-test (the structural lock):** assert every section excluded from verbatim-extraction is enrolled in L1 Check-9's determinism set (or another named invariant). Fails if an excluded section is covered by neither gate. This closes the "escapes verbatim AND escapes determinism" hole.
3. **07G presence/shape assertion** (Amelia): the generated `-gen` pack contains a 07G section with a non-empty body in the expected ordinal position (after 07F, before 08).
4. **Formal rule comment** in the test stating the principled rule: verbatim-extraction applies to frozen-origin sections; net-new `-gen` sections are governed by Check-9. Future net-new sections inherit the rule via the allowlist with zero further test edits.
> Note: expanding the verbatim-REQUIRED set is dev authority (safe direction); SHRINKING it (adding an exclusion) is party-mode governance — this 07G addition is already party-ratified (2026-06-20).

---

## SHOULD-FIX (fold into the same cycle)
- **Two-lane CI not wired:** `quarantined` marker doesn't appear in `pyproject.toml` `addopts` (`-m 'not live and not serial'`), so repeatability runs on the blocking lane. Either deselect `quarantined` in addopts (if non-blocking is intended) or drop the marker and accept blocking — make the marker's promise real.
- **Silent-drift canary** (`test_vision_silent_drift_canary.py`): replace the `compare_artifacts(payload, payload)` self-compare with a comparison against a stored golden so it can actually detect drift.
- **Provider `slide_id` (`provider.py`):** replace `setdefault` with a fail-loud equality check (`response slide_id == requested`) so a provider can't silently mislabel a slide.
- **Provider model-id:** validate the response `provider_model_id` against the pinned/requested id; reconcile `model_config.yaml` (`gpt-5`) vs the hard-pinned `DEFAULT_MODEL_ID="vision-fixture-v1"` so model resolution and the actual call agree.
- **Retry coverage (Edge M1/M2):** include 429/408 and connection errors (`ConnectError`/`ReadError`) in the bounded transport-only retry (currently only `>=5xx` + `TimeoutException`).

## NIT (reviewer discretion; close if cheap)
`confidence_score` is accepted but never consulted (wire it into `_assert_perceived` or document it as advisory); partial-batch failure aborts the whole node (consider emitting already-perceived artifacts + per-slide error state); bound `_levenshtein`/regex over `extracted_text`; photo-only text-free slide false-positives on narrated figures; PNG path run-dir containment check.

---

## Handoff requirements (binding — re-T11 rejects otherwise)
- **Baseline-diff attestation (Mary):** for ANY test you label "pre-existing / unrelated drift", paste clean-HEAD evidence (checkout `4455c04` or `git stash` and run the node) showing it is RED there too. Unattested "pre-existing" labels are rejected and the failure is treated as P2-2-introduced. (This is the discipline that caught F2 — it was bucketed as pre-existing but is RED only on the P2-2 tree.)
- **F1 mutation table** pasted in Completion Notes (per-threshold red↔green proof).
- Full battery green on the P2-2 tree EXCEPT the documented pre-existing set (5 parity + 14 contracts on clean HEAD `4455c04`); `test_33_1a` must be GREEN after the Option-A fix.
- `git diff --check` clean; ruff clean on touched surfaces; lint-imports 0-broken; lockstep L1 exit 0; frozen-pack-SHA unchanged.
- Do NOT add any detector/fidelity tag to `_RETRYABLE_DISPATCH_TAGS` (standing guard test must stay green).
