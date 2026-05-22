# Codex dev-story prompt — Story 34-1 (§02A → Texas Wrangler Subprocess Integration Round-Trip Test; Epic 34 Quinn-synthesis Option 5 load-bearing ratchet; cross-agent MANDATORY)

**Cycle:** Claude spec (with locked contract decisions D1-D8 per Round-1 SCP-ratification party-mode 4-of-4 APPROVE-with-amendments 2026-05-22) → Codex T1-T9 + T10 self-review → Codex drops `_bmad-output/implementation-artifacts/_codex-handoff/34-1.ready-for-review.md` → **Claude T11 cross-agent MANDATORY `bmad-code-review`** → Claude commit + flip done.
**Wave:** 1 — slot 1 (FIRST story in Epic 34; load-bearing integration ratchet for all 6 downstream stories per Quinn synthesis Option 5).
**Pre-authored:** 2026-05-22 immediately after C1 substrate amendment landed at commit `3159a0e`.
**Dispatch ordering:** **DISPATCH IMMEDIATELY post-C1** (no predecessor story dependencies; C1 allowlist amendment is the only prerequisite, and it's already committed + pushed).
**AMELIA-P2 freshness check at dispatch:** verify `git log -1` HEAD is `3159a0e` or descendant; verify TW-7c-4 PASS on the working tree at dispatch start.

---

```
Run bmad-dev-story on Story 34-1 (Epic 34 Wave 1; dual-gate; cross-agent code-review MANDATORY; §02A → Texas wrangler subprocess integration round-trip test + temporary in-tree translator scaffold — Quinn-synthesis Option 5 load-bearing ratchet for all 6 downstream Epic-34 stories).

## ⚠️ CONTRACT-LOCKED STORY — D1-D8 ARE LOCKED AT SPEC-AUTHOR; DO NOT RELITIGATE.

The spec at `_bmad-output/implementation-artifacts/migration-34-1-section-02a-wrangler-integration-roundtrip-test.md` carries 8 LOCKED contract decisions (D1-D8) per Round-1 SCP-ratification 2026-05-22 (4-of-4 APPROVE-with-amendments; NO impasse; consensus held). Your job: implement per the contract. If you disagree with a decision OR find an implementation-time obstacle, surface as `decision_needed` at T10 self-review BEFORE completing — do NOT silently deviate. T11 cross-agent review verifies contract compliance, NOT contract negotiation.

## Required reading (read in order; do NOT skip)

1. **Story spec:** `_bmad-output/implementation-artifacts/migration-34-1-section-02a-wrangler-integration-roundtrip-test.md` (status: ready-for-dev; §Contract Negotiation Decisions D1-D8 are LOCKED; 6 ACs A-F; 11 task groups T1-T11).
2. **Epic 34 spec:** `_bmad-output/planning-artifacts/epics-section-02a-downstream-coherence.md` (the Epic this story slots into; AC-34-1-A through AC-34-1-F live there; NFR-E34-1/7/10 are load-bearing for this story).
3. **Phase A probe (drift inventory):** `_bmad-output/planning-artifacts/phase-a-probe-2026-05-22-section-02a-downstream-coherence.md` — the 6 drift items D1-D6 your translator scaffold must bridge.
4. **Phase B consensus (Quinn synthesis):** `_bmad-output/planning-artifacts/phase-b-consensus-2026-05-22-section-02a-downstream-coherence.md` — the ratified Option 5 mechanism your scaffold serves.
5. **Substrate amendment SCP (C1 committed `3159a0e`):** `_bmad-output/planning-artifacts/sprint-change-proposal-2026-05-22-epic-34-substrate-amendment.md` — the 27-path allowlist; your touched files are inside the envelope.
6. **Trial-3 attempt-2 forensic anchor (the directive this Epic was born to fix):**
   - `state/config/runs/6a3393f8-f369-4a30-b7c1-b50c60c1d1a2/directive.yaml` — sha256 `351a57fbe12aff4a49349c4a646618d92ae38a798ec53eee61668f74f8bbd703`; gitignored; T2 fixture-copy target. If absent, HALT-AND-SURFACE per spec D7.
   - `state/config/runs/6a3393f8-f369-4a30-b7c1-b50c60c1d1a2/run.json` — trial envelope at crash moment (auxiliary; for context).
7. **§02A composer baseline (the upstream you do NOT modify):**
   - `app/composers/section_02a/composer.py` — the LLM-driven directive composition body (READ ONLY).
   - `app/composers/section_02a/directive_model.py` — `Directive` + `DirectiveSource` Pydantic v2 models (READ ONLY; your test imports `Directive` for fixture-replay).
   - `app/composers/section_02a/cli_adapter.py` — the trial-CLI bridge (READ ONLY).
8. **Texas wrangler baseline (the downstream you do NOT modify):**
   - `skills/bmad-agent-texas/scripts/run_wrangler.py` lines 280-394 (input validator — the drift surface your translator bridges).
   - Lines 1660-1738 (result.yaml writer — the output your test asserts against).
   - Lines 1240-1266 (metadata.json writer — the source of the `sme_refs[]` forward-contract assertion).
9. **Pipeline-manifest regime (per Epic 33 Standing Regime; AMELIA-RISK-3 from SCP-ratification):**
   - `docs/dev-guide/pipeline-manifest-regime.md` — touches `app/composers/section_02a/` MAY fall under `block_mode_trigger_paths`. Read at T1 before opening any file.
10. **Required readings:**
    - `docs/dev-guide/pydantic-v2-schema-checklist.md` — translator is NOT Pydantic but the test reuses §02A's Pydantic `Directive` model.
    - `docs/dev-guide/dev-agent-anti-patterns.md` — A11 Windows-portability + A9 vacuous-test passes (the A9 mitigation in AC-34-1-A is binding).
    - `docs/dev-guide/story-cycle-efficiency.md` — K-discipline 1.5× target ≈ ~7.5K LOC ceiling.
11. **Governance JSON entry** (if not yet present, surface decision_needed for operator to register Story 34-1 in `docs/dev-guide/migration-story-governance.json` with `dual-gate; cross_agent_review_required=true; expected_pts=5; expected_k_target=1.5; r_tier=R2; t11_tier=cross-agent; lookahead_tier=2; prerequisite_stories=[]` — Story 34-1 has no predecessor stories within Epic 34; C1 substrate amendment is the prerequisite and is already done).
12. **Sandbox-AC inventory:** `docs/dev-guide/migration-ac-sandbox-inventory.json` — confirm `subprocess` + `sys.executable` invocations are in `dev_agent_available` (they are).
13. **C1 substrate amendment (the path-envelope you operate within):** `tests/audit/test_audit_tw_7c_4_no_live_dispatch_scope_creep.py` — read the comments at the §"Epic 34 §02A downstream-consumer coherence amendment 2026-05-22" block to confirm your touched paths are pre-allowlisted.

## T1 hard checkpoints (HALT-AND-SURFACE if violated)

- C1 substrate amendment at commit `3159a0e` is HEAD or ancestor of HEAD. Verify: `git log --oneline --all | grep 3159a0e`. If C1 has been reverted, HALT-AND-SURFACE.
- Trial-3 attempt-2 forensic fixture exists at `state/config/runs/6a3393f8-f369-4a30-b7c1-b50c60c1d1a2/directive.yaml`. If absent (operator may have cleaned up gitignored runs/), HALT-AND-SURFACE per spec D7.
- Wrangler exists at `skills/bmad-agent-texas/scripts/run_wrangler.py` AND is invokable as a subprocess via `.\.venv\Scripts\python.exe skills/bmad-agent-texas/scripts/run_wrangler.py --help` (should exit 0 with usage text).
- §02A composer importable: `.\.venv\Scripts\python.exe -c "from app.composers.section_02a.directive_model import Directive; print('OK')"` resolves cleanly.
- `tests/integration/` directory may or may not exist; if it doesn't, create with `__init__.py`. Already allowlisted at C1.
- `tests/fixtures/integration/section_02a/` directory does NOT exist yet; you create it at T2. Allowlisted at C1 (the `__init__.py` + `conftest.py` paths are pre-bound; data fixtures like `forensic_directive_trial_3_attempt_2.yaml` are non-`.py` so they're not subject to the dual-predicate).
- Class-conformance: 11 contracts unchanged (no model changes in this story).
- lint-imports: 12-13 KEPT unchanged (no new import-linter contracts in this story).
- TW-7c-4 dual-predicate test PASS on working tree at dispatch start (allows you to verify mid-implementation that you haven't drifted out of allowlist).

## Files in scope

**New (~6 files):**
- `app/composers/section_02a/_wrangler_translator.py` (NEW; D1/D2/D3/D4 contract; ~80-120 LOC).
- `tests/integration/__init__.py` (NEW IF doesn't exist; package marker; 0 LOC body).
- `tests/integration/test_section_02a_to_wrangler_subprocess_roundtrip.py` (NEW; D5/D6 contract; ~150-200 LOC including 3 test functions per D6 template).
- `tests/fixtures/integration/__init__.py` (NEW; package marker; 0 LOC body).
- `tests/fixtures/integration/section_02a/__init__.py` (NEW; package marker; 0 LOC body).
- `tests/fixtures/integration/section_02a/forensic_directive_trial_3_attempt_2.yaml` (NEW; byte-identical copy of forensic directive per D7).

**Modified (0 files in production code; 1 optional T8 doc update):**
- (optional T8; defer if K-budget tight) `docs/dev-guide/specialist-anti-patterns.md` — file a one-line cross-reference noting Story 34-1 as the first §02A→wrangler integration green test.

**Do NOT modify:**
- `app/composers/section_02a/composer.py` (Story 34-3 surface; READ ONLY).
- `app/composers/section_02a/directive_model.py` (Story 34-3 surface; READ ONLY — but you DO import `Directive` for fixture-replay; that's read-only via import).
- `app/composers/section_02a/cli_adapter.py` (already wired; READ ONLY).
- `skills/bmad-agent-texas/scripts/run_wrangler.py` (Stories 34-2/34-4 surface; READ ONLY — but you DO invoke as subprocess; that's read-only via subprocess.run).
- §02A composer 12-test suite (Story 34-3 surface; READ ONLY).
- M-A1 wiring-contract tests at `tests/marcus_cli/test_compose_section_02a_directive_adapter.py` (Story 34-3 surface; READ ONLY).
- `app/marcus/orchestrator/directive_composer.py` (Story 34-6 deletion target; READ ONLY at T1 if you want to understand the legacy composer's vocab, but DO NOT touch).
- TW-7c-4 allowlist at `tests/audit/test_audit_tw_7c_4_no_live_dispatch_scope_creep.py` (C1 already amended; no further changes needed for Story 34-1).

**Do NOT introduce:**
- New third-party deps. `pytest`, `subprocess`, `sys`, `pathlib`, `hashlib`, `yaml` (PyYAML; already in deps) are sufficient.
- Live-LLM calls in any test in this story. Fixture-replay only. AC-34-1-F (operator-gated live-LLM) is OUT OF SCOPE for dev-agent.
- Imports of `app.marcus.orchestrator.directive_composer` (legacy composer; do NOT import).
- Imports of `app.composers.section_02a._wrangler_translator` from any non-test, non-cli_adapter path. The translator is private (underscore-prefixed); test imports + (optional) cli_adapter imports are the ONLY allowed call sites.
- Mock of the wrangler subprocess. Real subprocess via `subprocess.run([sys.executable, ...])` is mandatory per M-Murat-1 binding.
- Mock of the directive write path. Real `tmp_path/directive.yaml` write is mandatory per AC-34-1-A.
- Mock of `translate_directive_for_wrangler`. Real call is mandatory per AC-34-1-C.
- Defensive `serial` markers on tests (post-7c.0c xdist defaults apply; only add if a 34-1 test empirically fails under xdist).
- New entries in `PERMITTED_PYTHON_DIFFS`. C1 has pre-allowlisted everything Story 34-1 needs.

## Critical implementation notes

- **Contract decisions D1-D8 are LOCKED.** If implementation surfaces a need to deviate, surface as `decision_needed` at T10 self-review BEFORE completing. Do NOT silently deviate.
- **K-target 1.5× ≈ ~7.5K LOC ceiling.** Estimate ~200-400 LOC across all files. Comfortable headroom; well below ceiling.
- **Cross-agent MANDATORY at T11** — Claude reviews FULL diff in fresh context per Murat M-Murat-1. T10 self-review is supplemental.
- **Murat new-A9-surface-1 mitigation in AC-34-1-A (BINDING):** the test MUST assert `len(materials) >= 1` BEFORE asserting per-row shape. Without this, an empty-materials case could vacuously pass the "at least one row" check.
- **Murat new-A9-surface-2 mitigation in AC-34-5-A (preserve at Story-34-1 close):** `TRANSLATOR_ACTIVE_MAPPINGS` MUST be read at runtime by `translate_directive_for_wrangler` (not just declared at module-top). Your translator implementation MUST gate each mapping on membership in the frozenset; Story 34-5's test will assert this via `inspect.getsource()` grep.
- **Trial-3 attempt-2 forensic-anchor (AC-34-1-B BINDING):** the test MUST assert byte-identical sha256 match against `351a57fbe12aff4a49349c4a646618d92ae38a798ec53eee61668f74f8bbd703`. If your local fixture-copy drifts (e.g., line-ending normalization on Windows), the test fails — and that's correct behavior. Verify the copy with `Get-FileHash` or `sha256sum` BEFORE running the test.
- **Translator scaffolding markers (AC-34-1-C + Story-34-7 AC-34-7-H BINDING):** the translator file MUST contain `__epic_34_scaffolding__ = True` (module-level) AND `# DELETE-AT-EPIC-34-CLOSE — SCAFFOLDING` (docstring). Story 34-7's forensic sweep does `grep -rn "__epic_34_scaffolding__" .` and `grep -rn "DELETE-AT-EPIC-34-CLOSE" .` expecting 0 hits post-deletion; the presence at Story 34-1 close is the deletion-target marker.
- **Mock-surface audit (AC-34-1-D BINDING):** every mock the test uses MUST be enumerated in the test docstring with rationale. The ONLY acceptable mock is the upstream LLM call (which fixture-replay obviates anyway). Do NOT mock: the wrangler subprocess, the directive write path, the translator function, or the §02A Directive model.
- **Sandbox-AC discipline (AC-34-1-F = operator-gated; per CLAUDE.md):** AC-34-1-A through AC-34-1-E are dev-agent verifiable (no live LLM, no operator-only CLIs). AC-34-1-F is operator-gated (live-LLM exercise on real Tejal corpus); dev-agent SHALL NOT exercise live LLM. The sandbox-AC validator (`scripts/utilities/validate_migration_story_sandbox_acs.py`) will inspect this split at ready-for-dev finalization.
- **Pipeline-lockstep regime (AMELIA-RISK-3 from SCP-ratification):** read `docs/dev-guide/pipeline-manifest-regime.md` at T1 before touching `app/composers/section_02a/`. The translator's creation MAY trigger block-mode evaluation; Cora's hook (`skills/bmad-agent-cora/scripts/preclosure_hook.py`) is the gate. Surface decision_needed if hook fires unexpectedly.
- **Forensic fixture copy mechanism (D7):** use the `cp` or `Copy-Item` command from D7 verbatim. The fixture is gitignored AT SOURCE (state/config/runs/) but the COPY at tests/fixtures/integration/ is normally tracked. Verify sha256 match BEFORE committing.

## T1.5 contract verification gate

Before opening any code file, verify the contract is implementable:

1. Read `app/composers/section_02a/directive_model.py` fully. Confirm `Directive` and `DirectiveSource` are importable as named in D6 (lines 109-128 + lines 53-106). If signature drifts (Story 34-3 may move them), surface decision_needed.
2. Read `skills/bmad-agent-texas/scripts/run_wrangler.py` lines 280-394 fully. Confirm the validator expects fields named `ref_id` + `role` + `provider` + `locator` + (for retrieval-shape) `intent` + `provider_hints`. If wrangler's expected shape has drifted (Story 34-2 may have landed earlier than expected), surface decision_needed.
3. Run the wrangler subprocess manually with the forensic directive fixture (after T2 copy) to confirm the exit-30 crash reproduces:
   ```
   .\.venv\Scripts\python.exe skills\bmad-agent-texas\scripts\run_wrangler.py `
       --directive tests\fixtures\integration\section_02a\forensic_directive_trial_3_attempt_2.yaml `
       --bundle-dir <tmp-dir> --json
   ```
   Expected: exit 30 with `[run_wrangler] directive error: sources[0] missing required field: ref_id` in stdout. If the crash does NOT reproduce, the forensic anchor has drifted from the documented state — surface decision_needed.

## T9 self-conducted G6 layered review (Codex; binding mock-surface audit per AC-34-1-D)

When you reach T9, conduct a self-review with three layers:

**Blind Hunter:** read the test + translator with no spec context; look for obvious bugs.
- Does `len(materials) >= 1` get asserted BEFORE the row-shape assertions? (A9 mitigation)
- Does the test use real subprocess (not mocked)?
- Are all paths repo-relative + tested with `Path` objects?

**Edge Case Hunter:** walk every branching path.
- What happens if forensic fixture is missing? (test should explicitly skip with reason, not silent-fail)
- What happens if wrangler subprocess hangs? (subprocess.run has a default timeout? Add explicit `timeout=` if needed)
- What happens if the translator's mappings drift between Story 34-1 and Story 34-2? (test should reflect current state; Story 34-2 updates the test in lockstep)
- What happens on Windows vs POSIX? (path separators; subprocess invocation cwd; UTF-8 encoding)

**Acceptance Auditor:** verify each AC against the test.
- AC-34-1-A: ✓ subprocess + materials-non-empty + row-shape + sme_refs forward-contract
- AC-34-1-B: ✓ forensic sha256 byte-identical match
- AC-34-1-C: ✓ translator file with `__epic_34_scaffolding__ = True` + DELETE-AT-EPIC-34-CLOSE marker
- AC-34-1-D: ✓ mock-surface enumeration in test docstring
- AC-34-1-E: ✓ pytest exit 0 with >=3 tests passing

**Mandatory output:** `_bmad-output/implementation-artifacts/_codex-handoff/34-1.ready-for-review.md` with three sections (one per layer) + a final mock-surface audit table enumerating every mock + rationale.

## T10 ready-for-review handoff

When T9 is complete and all ACs are satisfied:

1. Flip `migration-34-1-section-02a-wrangler-integration-roundtrip-test` to `review` status in `_bmad-output/implementation-artifacts/sprint-status.yaml`.
2. Write handoff at `_bmad-output/implementation-artifacts/_codex-handoff/34-1.ready-for-review.md` per T9 output spec.
3. Run broad regression sweep + report delta vs 88-baseline per SCP §5 abort tripwire.
4. Surface ANY contract deviation OR any `decision_needed` BEFORE completing.

## T11 cross-agent review handoff (Claude — for orchestrator reference; not Codex action)

Claude T11 will:
- Read FULL diff in fresh context.
- Verify D1-D8 contract compliance.
- Verify mock-surface audit (AC-34-1-D) is faithful + complete.
- Verify forensic-anchor sha256 byte-identical (AC-34-1-B).
- Verify A9 mitigation (`len(materials) >= 1` before row-shape; AC-34-1-A).
- Verify scaffolding markers (`__epic_34_scaffolding__` + DELETE-AT-EPIC-34-CLOSE; AC-34-1-C).
- Verify TRANSLATOR_ACTIVE_MAPPINGS production-load-bearing (precursor to AC-34-5-A).
- Run focused suite + broad regression sweep.
- Commit + flip Story 34-1 done.
- File any deferred-inventory entries for surfaced findings.

## Cycle-close discipline

Once Claude T11 commits + flips done, the operator-driven next step is:

1. Verify Story 34-1 round-trip test stays GREEN on a fresh `pytest tests/integration/test_section_02a_to_wrangler_subprocess_roundtrip.py` run.
2. Dispatch Story 34-2 (wrangler 6-role union + excluded_reason + cross-field invariants) per Quinn-synthesis Option 5 sequencing.
3. Continue Stories 34-2 → 34-3 → 34-4 → 34-5 → 34-6 → 34-7 with Story 34-1's ratchet running continuously underneath each.

---

## Reference appendix: forensic directive shape (read-only context)

The Trial-3 attempt-2 forensic directive at `state/config/runs/6a3393f8-.../directive.yaml` (sha256 `351a57fbe12aff4a49349c4a646618d92ae38a798ec53eee61668f74f8bbd703`; 4192 bytes; 11 sources) has the following shape (paraphrased from next-session-start-here.md):

```yaml
run_id: <UUID4>
corpus_dir: course-content/courses/tejal-apc-c1-m1-p2-trends/
sources:
  - src_id: src-001          # WRANGLER REJECTS: wants `ref_id`
    locator: <relative-path>
    provider: local_file
    role: primary            # OK (wrangler accepts `primary`)
    description: <LLM-judged>
    expected_min_words: <int>
  - src_id: src-002
    locator: <relative-path>
    provider: local_file
    role: supporting         # WRANGLER REJECTS: wants `supplementary`
    description: <LLM-judged>
    expected_min_words: <int>
  # ... 9 more sources with src_id, role=supporting (no ignored rows in Tejal corpus)
composed_at: <tz-aware-datetime>
schema_version: 1
```

Your translator's job is to produce this transformed shape that the wrangler accepts:

```yaml
run_id: <UUID4>  # unchanged
sources:
  - ref_id: src-001          # mapped from src_id
    locator: <relative-path>
    provider: local_file
    role: primary            # unchanged
    description: <LLM-judged>
    expected_min_words: <int>
  - ref_id: src-002          # mapped
    locator: <relative-path>
    provider: local_file
    role: supplementary      # mapped from supporting
    description: <LLM-judged>
    expected_min_words: <int>
  # ... 9 more
# corpus_dir, composed_at, schema_version: wrangler ignores extras (or accept-or-strip per Codex implementation)
```

If the wrangler rejects extras (`extra="forbid"` Pydantic at wrangler side; check during T1.5), strip them before write. If it accepts extras, leave them in.

---

**Authored 2026-05-22 by Claude orchestrator post-C1 commit `3159a0e`. Ready for Codex dispatch.**
```
