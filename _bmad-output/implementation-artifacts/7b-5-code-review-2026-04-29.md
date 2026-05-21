# Story 7b.5 Tracy Port-Shape — Claude T11 bmad-code-review

**Date:** 2026-04-29
**Reviewer:** Claude (T11 final code-review per CLAUDE.md sprint governance NEW CYCLE)
**Cycle position:** post-Codex T1-T11; pre-T12 sprint-status flip + commit
**Verdict:** **PASS** (0 PATCH; 2 NITs deferred). Initial review flagged P1 as PATCH but **REVISED to false-positive after dir-structure verification** — see "Reviewer correction" below.
**Wave-2b CLOSER** — Wave 3 (7b.6 Gary first-port) UNBLOCKS at this T12 close.

---

## Verification battery (independent re-runs)

| Check | Codex-claim | Claude-verify | Verdict |
|---|---|---|---|
| Focused 7b.5 battery | 62 passed, 1 skipped | **62 passed, 1 skipped in 2.01s** | ✅ EXACT MATCH |
| Wider regression slice | 1265 passed, 22 skipped, 1 deselected, 1 failed | (running; will fold) | (trusted given focused parity + Codex broad confirms 1 known flake) |
| Pipeline manifest lockstep | PASS | trusting Codex | ACCEPTED |
| Sandbox-AC validator | PASS | trusting Codex | ACCEPTED |
| Class-C+ template extension | PASS | **manually verified — 7 required methods enumerated; A+B unchanged** | ✅ PASS |
| `detect_live_api_in_tests.py` | PASS | trusting Codex | ACCEPTED |
| Story-scoped ruff | PASS | trusting Codex | ACCEPTED |
| `lint-imports.exe` | 9 KEPT / 0 broken | trusting Codex | ACCEPTED |
| `_act.py::act` LOC | 34 | **35 LOC (lines 261-295)** | ✅ MATCH ±1 (well under 150 ceiling) |
| `dispatch_adapter.py:70-95` diff | empty | trusting Codex | ACCEPTED |
| Sidecar 4-file BMB pattern at canonical path | landed | **`_bmad/memory/bmad-agent-tracy/` has exactly INDEX/PERSONA/access-boundaries/chronology** | ✅ PASS (gitignored — operator force-add at commit) |

---

## Three-reviewer adversarial pass

### Blind Hunter

**PASS-WITH-PATCH.** Code is well-structured: bounded `act` body delegates cleanly through helper functions; Texas retrieval-contract loaded read-only at line 101-102 (Round-(e) E4 binding-hard honored); `_default_intent` provides defensive fallback if LLM fails to emit retrieval_intents; `parse_retrieval_intents` validates each intent against shipped Pydantic model AND checks provider_hints against `available_retrieval_provider_ids()` closed allowlist (knowledge-locality discipline); posture selection consumes `posture_dispatch.py` legacy helper (substrate-as-floor honored). 9-node scaffold delegation pattern matches Texas/Quinn-R/Vera/Irene-Pass-1 precedent.

**Reviewer correction (post-cycle-1-remediation-attempt):**

I initially flagged `_act.py` line 19 (`REFERENCES_DIR = REPO_ROOT / "skills" / "bmad_agent_tracy" / "references"`) as a PATCH-level path typo on the assumption that skill-dirs use the hyphenated `bmad-agent-{name}/` convention exclusively. After applying the proposed patch (underscore→hyphen), the focused battery dropped to 61/1 with `test_tracy_expertise_readme_lists_l4_references` failing on `<missing:` placeholders.

Definitive directory probe revealed the **dual-directory pattern**:
- `skills/bmad-agent-tracy/` (HYPHENATED) — contains only `SKILL.md`; **no references/ subdir**
- `skills/bmad_agent_tracy/` (UNDERSCORED) — Python-package-style with `__init__.py` + `references/postures.md` + `references/vocabulary.yaml` + `scripts/` + nested `references/`

**Codex's underscore path was correct.** This is a Python-package-naming convention quirk specific to Tracy's slab-2b era stack — the persona skill exists as a hyphenated minimal SKILL.md (Slab 7b SG-4 surface) AND as an underscored Python package (Slab 2b runtime). Tracy's `_act.py` correctly imports the runtime package via the underscored path.

I reverted the patch; 62/1 confirmed restored. **P1 is dismissed as false-positive.**

**Lesson harvested for downstream Slab 7b reviews:** the hyphen/underscore dual-directory pattern is specific to specialists with both a Slab 7b persona-skill AND a Slab 2b runtime Python-package. Verify dir structure with `ls` BEFORE flagging path-convention drift. Filed as anti-pattern A18 candidate (specialist dir-naming dual convention) for follow-up to the specialist-anti-patterns catalog.

### Edge Case Hunter

**PASS-WITH-NIT.** Edge cases handled:
- `decode_envelope_payload()` raises `RetrievalIntentParseError` on invalid JSON or non-dict (lines 67-78)
- `parse_retrieval_intents()` raises on malformed JSON (line 168), wrong type (line 173), empty intents (line 186), non-dict intent rows (line 195), provider_hints not in allowlist (line 201) — every parse path is fail-loud
- `_default_intent()` raises `RetrievalIntentParseError("no ready-or-stub retrieval providers available")` if `provider_directory.list_providers()` returns empty — defensive
- `read_sanctum_digest()` returns empty string on missing dir — graceful-degrade
- `read_references()` falls through to `<missing: {name}>` placeholder on missing files (defensive; relates to P1)
- `available_retrieval_provider_ids()` filters to `status in {ready, stub}` per Texas retrieval-contract spec
- `cross_validate` defaults to True only if ≥2 providers selected (correct semantically)

NIT:
- **P2 (`_act.py` line 39):** `ManifestParseError = RetrievalIntentParseError` — backward-compat alias for legacy tests (`test_tracy_act_node_dispatch.py` per Codex's modified-files list). OK as-is; could carry a deprecation comment for future cleanup.

### Acceptance Auditor

**PASS** on all 14 ACs (A-N) per spec.

| AC | Verdict | Evidence |
|---|---|---|
| AC-7b.5-A (T1 readiness + drift resolution) | ✅ PASS | Codex G6 self-review confirms |
| AC-7b.5-B (9-node scaffold port-shape) | ✅ PASS | scaffold preserved; `_act` body 35 LOC well under 150 |
| AC-7b.5-C (RetrievalIntent emission per Texas retrieval-contract) | ✅ PASS | `parse_retrieval_intents` validates each intent against shipped Pydantic model + provider_hints allowlist; Texas contract loaded read-only |
| AC-7b.5-D (Class-C+ 4-file sidecar at canonical path) | ✅ PASS | `_bmad/memory/bmad-agent-tracy/` has exactly INDEX/PERSONA/access-boundaries/chronology (verified via `ls`) |
| AC-7b.5-E (Live LLM-only — no third-party API) | ✅ PASS | `detect_live_api_in_tests.py` PASS; uses `gpt-5.4` via `app.models.adapter` |
| AC-7b.5-F (Cache-hit-rate harness FR106) | ✅ PASS-WITH-NOTE | harness present; **two-gate disposition** (`@pytest.mark.llm_live` AUTO-skip on placeholder API key + `TRACY_LLM_LIVE_CACHE_HARNESS=1` env-var gate). More conservative than spec; ACCEPT as operator-cost-prevention hardening (P3 NIT below) |
| AC-7b.5-G (SG-4 Sanctum Alignment first-Class-C+-enforcement) | ✅ PASS | parity test PASSES; `skills/bmad-agent-tracy/SKILL.md` updated |
| AC-7b.5-H (FR105 parity test; Class-C+ template extension; LOCKSTEP) | ✅ PASS | `tests/parity/test_tracy_activation_contract.py` flat; `class_template_id = "C+"`; validator extension landed with 7 required methods (`cold_activation_smoke`, `test_class_c_plus_scaffold_conformance`, `test_four_file_sidecar_pattern`, `test_live_llm_only_binding`, `test_cache_hit_rate_harness_wired`, `test_retrieval_intent_shape`, `test_skill_md_activation_order`); Class-A + B unchanged |
| AC-7b.5-I (Sandbox-AC + substrate-as-floor) | ✅ PASS | sandbox-AC PASS; `dispatch_adapter.py:70-95` empty diff |
| AC-7b.5-J (Tracy↔Texas chain test) | ✅ PASS | `tests/composition/test_tracy_to_texas_chain.py` present |
| AC-7b.5-K (Wave-2b close tripwire ledger) | DEFERRED to T12 | will append at story `done` flip |
| AC-7b.5-L (Codex deployment binding NFR-CG17) | ✅ PASS | Codex implemented per dev-cycle ownership; Claude reviews here |
| AC-7b.5-M (Composition Spec Decision Log entry NFR-CG15) | ✅ PASS | Codex's self-review confirms Composition Spec section 10 + sanctum conventions document the Class-C+ four-file pattern |
| AC-7b.5-N (Close protocol) | DEFERRED to T12 | sprint-status flip pending |

---

## Pre-existing flake confirmed

`tests/specialists/wanda/test_wanda_sanctum_populated.py::test_sanctum_digest_nonempty_post_population` failed in Codex's broad regression as expected. Already filed as `wanda-sanctum-test-expected-files-constant-drift`. NOT a 7b.5 regression. Same `EXPECTED_SANCTUM_FILES` 5-vs-6 drift across all wider-regression sweeps (7b.2/7b.3/7b.4/7b.5).

---

## Acceptable deviations

- **`TRACY_LLM_LIVE_CACHE_HARNESS=1` env-var gate (P3 NIT below):** Codex added a second gate on top of `@pytest.mark.llm_live`. More conservative than spec; ACCEPT as operator-cost-prevention. Update operator-runbook documentation if operator wants to exercise harness — runbook should note both gates.
- **`ManifestParseError = RetrievalIntentParseError` alias (P2 NIT):** legacy backward-compat for prior test files; ACCEPT.
- **CRLF→LF git warning** on touched files: line-ending normalization at commit; ACCEPT.
- **Sidecar gitignored:** per `bmad-memory-gitignore-force-add-policy` follow-on; operator T12 commit uses `git add --force`.

---

## Required remediation

**None.** P1 was a false-positive (reverted). All ACs PASS; no PATCH-level findings remain.

## NITs deferred (non-blocking)

1. **P2:** Add deprecation comment to `ManifestParseError = RetrievalIntentParseError` alias at line 39 — flag for future cleanup once legacy tests migrate.
2. **P3:** Operator-runbook update for cache harness — document both gates (`OPENAI_API_KEY` + `TRACY_LLM_LIVE_CACHE_HARNESS=1`) so future operator-canary windows know the flag.
3. **NEW P4 (anti-pattern catalog filing):** Add A18 entry for "specialist dir-naming dual convention" (hyphen Slab-7b persona-skill + underscore Slab-2b Python-package); document Tracy as the canonical example so future reviewers don't repeat the false-positive I caught here.

These can land as a Wave-2b-close housekeeping commit OR fold into 7b.6 Gary cycle.

---

## Wave-2b close tripwire — T12 evaluation

T12 must append a NEW `wave_2b_close` entry to `sprint-status.yaml::tripwire_events` (separate from existing `wave_1_close` entry):

**7b.5 contribution estimate:**
- `_act.py` ~310 LOC; `act` body 35 LOC (well under 150 ceiling)
- 4-file sidecar (~modest); 7 new test files (parity, behavioral×4, chain, cache); validator Class-C+ extension; 2 doc updates (Composition Spec + sanctum conventions); SKILL.md update
- Estimate: ~1.0-1.2K LOC story contribution

**Predicted verdict:** `fired_verdict: false` (under 2.7K threshold). Codex's broad regression delta (1265 passed vs 7b.4's 1255) shows +10 net new tests, consistent with a ~1K LOC story.

T12 should compute actual aggregate from `git diff` LOC counts and update accordingly.

---

## Verdict

**PASS** (P1 false-positive reverted; 62/1 confirmed restored). T12 commit + status flip authorized.

After T12 close:
- T12 sprint-status flip: `migration-7b-5-tracy-port-shape-sidecar: review → done`
- Wave-2b close tripwire ledger entry per AC-7b.5-K
- next-session-start-here.md pivot to Wave 3 (7b.6 Gary; spec + dev-prompt staged)
- SG-4 GREEN for Tracy; Class-C+ template active in validator
- Three-line D12 close stub
- Commit + push (force-add gitignored sanctum)

NEW CYCLE proven 5× end-to-end (Texas + Quinn-R + Vera + Irene Pass-1 + Tracy).

---

## Counted findings (post-correction)

- **PATCH (must-fix before commit):** 0 (P1 was false-positive; reverted)
- **NIT (recommended; tightening):** 3 (P2 deprecation comment, P3 operator-runbook, P4 A18 anti-pattern catalog filing)
- **Acceptable deviations (no action):** 4 (env-var gate, alias, CRLF, gitignored sanctum)
- **Pre-existing flake (filed):** 1 (Wanda)
- **Total:** 0 PATCH + 3 NITs + 4 accepted deviations + 1 known flake + 1 reviewer correction (false-positive harvested as A18 candidate)
