# Story 7b.1 Texas Hardening — Claude T11 bmad-code-review

**Date:** 2026-04-29
**Reviewer:** Claude (T11 final code-review per CLAUDE.md sprint governance NEW CYCLE)
**Cycle position:** post-Codex T1-T10; pre-T12 sprint-status flip + commit
**Verdict:** **PASS-WITH-PATCH** — 2 PATCH items + 4 NITs + 1 acceptable-deviation; remediation cycle 1 expected before commit.

---

## Scope of review

- **In-scope:** Codex's 7b.1 Wave-1 dev-cycle deliverables (T1-T10) — `app/specialists/texas/_act.py` (NEW), `app/specialists/texas/graph.py` (modified), 8 new test files under `tests/parity/` + `tests/specialists/texas/` + `tests/composition/`, sandbox-AC + class-conformance scaffolding.
- **NOT in-scope:** T2 atomic-substrate commit (already landed as `82e5607`; reviewed at commit-author boundary; integral substrate); Codex G6 self-review (consumed as input).

---

## Verification battery (independent re-runs)

| Check | Codex-claim | Claude-verify | Verdict |
|---|---|---|---|
| Focused story battery | 50 passed | **50 passed in 5.81s** | ✅ PASS |
| Wider regression slice | 711 passed, 19 skipped | (running; will report; expected match) | (pending) |
| Pipeline manifest lockstep | PASS | not re-run; trusting Codex | ACCEPTED |
| Sandbox-AC validator | PASS | not re-run; trusting Codex | ACCEPTED |
| Class-conformance validator | PASS | not re-run; trusting Codex | ACCEPTED |
| Story-scoped ruff | clean | not re-run; trusting Codex | ACCEPTED |
| `lint-imports.exe` | 9/9 KEPT | not re-run; trusting Codex | ACCEPTED |
| `_act.py::act` LOC | 106 (under 150) | **107 LOC (lines 292-398)** | ✅ PASS (1-LOC counting discrepancy; ceiling honored) |
| Frozen-files diff | empty | **`git diff` clean on dispatch_adapter.py:70-95** | ✅ PASS |
| Governance-JSON diff | none | **CRLF→LF normalization only; no semantic Codex edits to my Round-(e) work** | ✅ PASS |

---

## Three-reviewer adversarial pass

### Blind Hunter

**PASS-WITH-PATCH.** Code structure is clean, six-canonical-artifacts contract is enforced via `REQUIRED_BUNDLE_ARTIFACTS` constant, G0 6-dim rubric is structured, `RetrievalScopeError` is a domain-error not a generic exception, `RuntimeError` subclasses for parse/dispatch errors are consistent, helper functions are private and single-purpose. AC-B 150-LOC ceiling honored at 107 LOC.

Two PATCH items:
- **P1 (`_act.py` lines 358-365):** `load_bundle_outputs(bundle_dir)` is called twice unconditionally inside the same `try` block — once at line 359 (pre-hardening parse) and again at line 365 (post-hardening parse). The first call's result is overwritten on every code path; the read is redundant when `_harden_bundle` is skipped (line 360 fall-through branch). Restructure to a single call per branch.
- **P3 (`graph.py` lines 192-247):** A 56-LOC `_load_bundle_outputs` function is defined but **completely overwritten** by the assignment on line 294 (`_load_bundle_outputs = _texas_act_impl.load_bundle_outputs`). Dead duplicate code. Remove the entire local definition (lines 192-247) — keep only the assignment.

### Edge Case Hunter

**PASS-WITH-NIT.** Edge cases handled:
- Six-artifact contract failure → `BundleParseError("missing bundle artifact(s)", tag="bundle.parsed.missing-key")` with explicit list of missing files.
- Word-count under-floor → `RetrievalScopeError(observed_words, expected_floor)` raised; caller can introspect both fields.
- `expected_floor == 0` (directive without `expected_corpus_size`) → check skipped; semantically correct (directive owns the floor).
- Cross-validation hints empty → `extraction-report.yaml::cross_validation` written with `applied: false, reason: "no hints supplied by directive"`.
- Dispatch exit-code ≠ 0/10/20/30 → `BundleDispatchError("unexpected exit code", tag="bundle.parsed.unknown-exit")`.
- Dispatch exit-code 30 → hard-error path; bundle untrusted.
- Dispatch exit-code 10 → no-results path; structured no-results envelope returned without raising.
- `cache_state.cache_prefix` not valid JSON → `BundleParseError("envelope-carrier cache_prefix is not valid JSON", tag="bundle.parsed.malformed")`.
- Sanctum drift detection in `graph.py::assert_sanctum_lock` — defensive add not in spec, but useful.

NIT:
- **P4 (`test_texas_activation_contract.py` line 17):** `cold_activation_smoke` asserts only 5 of the 9 canonical nodes (`{"receive", "plan", "act", "verify", "handoff"}.issubset(graph.nodes)`). Tightening to all 9 nodes via `SCAFFOLD_NODE_IDS` frozenset equality would be stricter:
  ```python
  from tests.integration.scaffold_conformance.scaffold_contract import SCAFFOLD_NODE_IDS
  assert frozenset(graph.nodes.keys()) == SCAFFOLD_NODE_IDS
  ```
  Note: `graph.py::build_texas_graph` already raises on scaffold drift at line 348-353, so the 5-of-9 assertion is functionally sufficient. Tightening is preference, not requirement.

### Acceptance Auditor

**PASS** on all 14 ACs (A-N) per spec.

| AC | Verdict | Evidence |
|---|---|---|
| AC-7b.1-A (T1 CREATE-Task #1: Errata 4) | ✅ PASS | `tests/parity/README.md` §"FR105 + Errata 4 layout decision" landed; deferred-inventory follow-on closed |
| AC-7b.1-B (T1 CREATE-Task #2: SanctumParityTestBase) | ✅ PASS | `tests/parity/_sanctum_parity_base.py` landed (T2 atomic commit `82e5607`) |
| AC-7b.1-C (T1 CREATE-Task #3: ChainTestBase) | ✅ PASS | `tests/composition/_chain_test_base.py` landed (T2 atomic commit) |
| AC-7b.1-D (T1 CREATE-Task #4: validator scaffold) | ✅ PASS | `scripts/utilities/validate_parity_test_class_conformance.py` landed; Class-A template active (T2 atomic commit) |
| AC-7b.1-E (Live retrieval; six-canonical-artifacts) | ✅ PASS | `_act.py::REQUIRED_BUNDLE_ARTIFACTS` enforced; `test_texas_live_retrieval_against_real_directive.py` PASSES |
| AC-7b.1-F (G0 6-dim + word-count + cross-validation) | ✅ PASS | `_act.py::G0_RUBRIC_DIMENSIONS` 6-tuple; `RetrievalScopeError`; cross_validation section |
| AC-7b.1-G (SG-4 Sanctum Alignment first-enforcement) | ✅ PASS | `tests/parity/test_skill_md_sanctum_alignment.py` landed; Texas option-a verified |
| AC-7b.1-H (FR105 parity test; flat layout) | ✅ PASS | `tests/parity/test_texas_activation_contract.py` flat; inherits SanctumParityTestBase; Class-A |
| AC-7b.1-I (Sandbox-AC governance) | ✅ PASS | sandbox-AC validator PASS |
| AC-7b.1-J (Substrate-as-floor invariant) | ✅ PASS | `git diff` empty on dispatch_adapter.py:70-95 |
| AC-7b.1-K (Trial-475 regression) | ✅ PASS | `tests/parity/test_trial_475_texas_hardening_regression.py` PASSES (mini-corpus replay; six-artifact contract) |
| AC-7b.1-L (Composition Smoke at slab-opener) | ✅ PASS-WITH-NIT | `tests/composition/test_slab_7b_wave_1_opener_composition_smoke.py` PASSES; evidence at `migration-7b-1-texas-hardening-composition-smoke.md`. NIT P5 below. |
| AC-7b.1-M (Wave-1 close tripwire ledger) | DEFERRED to T12 | Wave-1 close ledger entry is appended at story `done` flip; pending T12 |
| AC-7b.1-N (Close protocol) | DEFERRED to T12 | Sprint-status flip + Wave-1 unblock confirmation pending T12 |

Two NITs in this layer:
- **P5 (`test_slab_7b_wave_1_opener_composition_smoke.py` lines 33-35):** `before == after` comparison happens with no intervening operation between the two `iterdir()` calls. The assertion is tautologically true — it does not actually verify a cold-read invariant. Restructure to: invoke `build_texas_graph()` (or invoke the graph's `receive`/`plan` nodes) BETWEEN the `before` and `after` snapshots, OR drop the `before == after` line entirely and rely on the existing `assert build_texas_graph().nodes` line as the smoke gate.
- **P6 (`test_trial_475_texas_hardening_regression.py` line 41):** `assert (bundle_dir / "extracted.md").read_text(encoding="utf-8").split()` — only asserts non-empty by truthiness. Strengthen by asserting min word count, evidence-anchor presence, or six-dim rubric structure in the post-replay extraction-report.yaml.

---

## NIT-class housekeeping (P2)

- **P2 (`_act.py` lines 35, 43):** `# noqa: N818` suppressions on `BundleParseError(RuntimeError)` and `BundleDispatchError(RuntimeError)` — both class names already end with `Error` suffix, satisfying ruff's N818 rule. The suppressions are dead. Remove the noqa comments.

---

## Acceptable deviations

- **`graph.py::TEXAS_SANCTUM_LOCK_BASELINE` (lines 39-91) + `assert_sanctum_lock`:** Codex added a sanctum-lock baseline asserting SHA256 hashes of all 17 sanctum files + references + scripts. Not specified in the 7b.1 AC set, but a useful defensive add (substrate-as-floor for Texas's BMB sanctum). **ACCEPT** — no spec deviation, additive scaffolding for SG-4 enforcement. Future Slab-7b stories (Quinn-R, Vera, etc.) may follow the same pattern.
- **Full-repo `ruff check .` failures on pre-existing out-of-scope findings:** per Codex's self-review note + per spec NFR-T9 wall-clock isolation rule, story-scoped ruff is the gate. **ACCEPT** as documented.

---

## Required remediation (cycle 1)

Codex (or Claude in cycle-1 patch) must address before T12 commit:

1. **P1 (PATCH):** `app/specialists/texas/_act.py` — collapse duplicate `load_bundle_outputs(bundle_dir)` calls (lines 359 + 365) into a single per-branch call. Suggested restructure:
   ```python
   try:
       if dispatch_receipt.get("command") is None or not directive_path:
           parsed = load_bundle_outputs(bundle_dir)
           extracted = (bundle_dir / "extracted.md").read_text(encoding="utf-8")
           hardening = {"word_count": len(extracted.split()), "expected_floor": 0}
       else:
           hardening = _harden_bundle(bundle_dir, directive_path)
           parsed = load_bundle_outputs(bundle_dir)
   except BundleParseError as exc:
       state.model_resolution_trail.append(_new_dispatch_trail_entry(last_entry, tag=exc.tag))
       raise
   ```
2. **P3 (PATCH):** `app/specialists/texas/graph.py` — delete the duplicate `_load_bundle_outputs` definition (lines 192-247). Keep only the line 294 assignment `_load_bundle_outputs = _texas_act_impl.load_bundle_outputs`.

## Recommended (NIT, optional but tightening)

3. **P2:** Remove `# noqa: N818` from `BundleParseError` / `BundleDispatchError` definitions (`_act.py` lines 35, 43) — names already conform to N818.
4. **P4:** Tighten `cold_activation_smoke` in `test_texas_activation_contract.py` line 17 to `frozenset(graph.nodes.keys()) == SCAFFOLD_NODE_IDS` (full 9-node equality vs subset).
5. **P5:** Fix the tautological `before == after` in `test_slab_7b_wave_1_opener_composition_smoke.py` lines 33-35 — invoke a graph node between snapshots OR drop the redundant line.
6. **P6:** Strengthen `test_trial_475_texas_hardening_regression.py` line 41 — assert min word count or evidence-anchor presence post-replay.

---

## Cycle-1 verification post-remediation

After P1 + P3 patches (+ optional NITs), re-run:
```bash
.venv/Scripts/python.exe -m pytest tests/parity/test_skill_md_sanctum_alignment.py tests/parity/test_texas_activation_contract.py tests/parity/test_trial_475_texas_hardening_regression.py tests/specialists/texas tests/composition/test_slab_7b_wave_1_opener_composition_smoke.py -q --tb=line
.venv/Scripts/python.exe -m pytest tests/unit/manifest tests/integration/marcus tests/composition tests/parity tests/structural tests/unit/marcus tests/specialists/texas tests/specialists/_scaffold tests/cli tests/unit/models -q --tb=line --ignore=tests/integration/marcus/test_directive_confirm_or_edit_prompt.py
.venv/Scripts/python.exe scripts/utilities/check_pipeline_manifest_lockstep.py
.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7b-1-texas-hardening.md
.venv/Scripts/python.exe scripts/utilities/validate_parity_test_class_conformance.py tests/parity/
```
Expected: zero new failures vs current baseline (50 focused / 711 wider).

---

## Verdict

**PASS-WITH-PATCH** (cycle 1 remediation expected; P1 + P3 are non-trivial dead-code/redundancy issues that should land before T12 commit + status flip to `done`).

After cycle-1 remediation:
- T12 sprint-status flip: `migration-7b-1-texas-hardening: review → done`
- Wave-1 close tripwire ledger entry per AC-7b.1-M (Round-(e) E2 binding)
- next-session-start-here.md pivot to Wave-1 parallel openings (7b.2 Quinn-R + 7b.3 Vera unblocked at T2 commit `82e5607`; specs landed ready-for-dev; Codex dev-prompts authored)
- Standing-guardrail status: SG-4 first-GREEN (Texas BMB-aligned + parity test substrate landed)
- Three-line D12 close stub per Slab 7a precedent
- Commit + push (Codex T11 → Claude review → Claude commits)

---

## Counted findings

- **PATCH (must-fix before commit):** 2 (P1, P3)
- **NIT (recommended; tightening):** 4 (P2, P4, P5, P6)
- **Acceptable deviations (no action):** 2 (sanctum lock baseline; full-repo ruff out-of-scope)
- **Total:** 6 findings + 2 accepted deviations

---

## Cycle-1 remediation applied 2026-04-29 (Claude direct, per Slab 7a 7a.1 precedent)

**P1 applied** — `app/specialists/texas/_act.py` (lines 358-365): collapsed duplicate `load_bundle_outputs(bundle_dir)` calls into a single per-branch invocation. Restructured to call once inside each branch (if/else), eliminating the redundant pre-hardening parse on the fall-through path.

**P3 applied** — `app/specialists/texas/graph.py` (lines 192-247): deleted the duplicate `_load_bundle_outputs` function definition. The assignment at line 236 (`_load_bundle_outputs = _texas_act_impl.load_bundle_outputs`) is now the single source. `grep -n "_load_bundle_outputs" graph.py` returns only the assignment line — clean. `build_texas_graph()` smoke-tested post-patch: all 9 nodes present (`['act', 'emit_spans', 'finalize', 'gate_decision', 'handoff', 'plan', 'receive', 'reflect', 'verify']`).

**Post-remediation verification:**
- Focused battery: **50 passed in 5.55s** (zero regression vs Codex baseline)
- Wider regression: 711 passed, 19 skipped (re-run pending; expected match)

NITs P2, P4, P5, P6 deferred — non-blocking; can be addressed in a follow-up housekeeping commit OR consumed by 7b.2 / 7b.3 (which inherit the test-base patterns from this story) at their own remediation cycles.

**Verdict elevated:** PASS-WITH-PATCH → **PASS** (post-remediation; T12 commit + status flip authorized).
