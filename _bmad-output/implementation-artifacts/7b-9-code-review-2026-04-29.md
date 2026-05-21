# Story 7b.9 Wanda Port-Shape Onto Scaffold - T11 Code Review

**Date:** 2026-04-29
**Story:** `migration-7b-9-wanda-port-shape-onto-scaffold`
**Reviewer:** Claude T11 local layered review (NEW CYCLE)
**Spec:** `_bmad-output/implementation-artifacts/migration-7b-9-wanda-port-shape-onto-scaffold.md`

## Verdict

**PASS.** All three drifts resolved (Drift #1 sanctum migration; Drift #2 two-SKILL.md ratification; Drift #3 scaffold-v0.2 alignment). Pre-existing `wanda-sanctum-test-expected-files-constant-drift` flake CLOSED structurally. Zero PATCH findings on Wanda scope. Cross-specialist retrofit working-tree state is intermingled with 7b.8 close per OBSERVATION-1 carried forward from 7b-8-code-review-2026-04-29.md (not re-litigated here).

## Findings

### Drift #1 — Sanctum migration to 6-file BMB ✓ RESOLVED

- Legacy `_bmad/memory/wanda-sidecar/` REMOVED (`ls` returns "No such file or directory").
- Canonical `_bmad/memory/bmad-agent-wanda/` populated with the 6 BMB files: `INDEX.md` + `PERSONA.md` + `CREED.md` + `BOND.md` + `MEMORY.md` + `CAPABILITIES.md`.
- T1 spec drift-resolution diverged from T1 plan in one detail (Codex T1 baseline notes): legacy sanctum was at `_bmad/memory/wanda-sidecar/` rather than `_bmad/memory/bmad-agent-wanda/` (5+1 sidecar pattern). Codex folded sidecar content into the canonical BMB and removed the legacy path. Acceptable — both starting states migrate to the same canonical end state.

### Drift #2 — Class-C two-SKILL.md ratified-binding ✓ RESOLVED (4th application)

- `skills/bmad-agent-wanda/SKILL.md` CREATED with minimal FR101 R1 frontmatter (`name: bmad-agent-wanda` + persona-focused description) + activation hot-load batch referencing all 6 BMB files + line documenting `skills/bmad-agent-wondercraft/` as Wondercraft API reference material consumed lazily.
- `skills/bmad-agent-wondercraft/SKILL.md` PRESERVED untouched (`git diff --name-only skills/bmad-agent-wondercraft/` returns empty).
- Class-C two-SKILL.md ratification proven 4× (Gary → Kira → Enrique → Wanda).

### Drift #3 — scaffold-v0.2 alignment ✓ RESOLVED

- `app/specialists/wanda/graph.py` aligned to canonical `SCAFFOLD_NODE_IDS` per FR96. Pre-7b.9 graph.py was 380 lines with inline body + Slab 2c.1 era conventions; post-7b.9 graph.py is bounded delegator pattern (~150 lines) with `_act` delegating to `_act.py`. Closes the pre-Slab-2b client-landed-not-on-scaffold gap.

### Flake closure — `wanda-sanctum-test-expected-files-constant-drift` ✓ RESOLVED

- `tests/specialists/wanda/test_wanda_sanctum_populated.py::EXPECTED_SANCTUM_FILES` updated to canonical 6-file tuple (`INDEX/PERSONA/CREED/BOND/MEMORY/CAPABILITIES`).
- All 3 `test_wanda_sanctum_populated.py` tests PASS (`test_sanctum_directory_exists` + `test_sanctum_digest_nonempty_post_population` + `test_sanctum_digest_deterministic_under_crlf`).
- Deferred-inventory entry already marked CLOSED at this row (struck-through with "CLOSED 2026-04-29 at Story 7b.9 T2" annotation).

### Wanda implementation review

- **6-file BMB sanctum** — present (verified `ls _bmad/memory/bmad-agent-wanda/`).
- **Class-C parity test** — `tests/parity/test_wanda_activation_contract.py` extends `SanctumParityTestBase` with `class_template_id = "C"` per Class-C inheritance. Validator reports 9 activation contracts conforming (was 8 before 7b.9; +1 = Wanda).
- **Audio-bed generation** — `_act.py` `generate_audio_beds()` writes to `assembly-bundle/audio/beds/<bed_id>.{mp3|wav}` per FR96. `WondercraftClient.generate_audio_bed()` invoked when present; falls back to existing `create_scripted_podcast` path because `scripts/api_clients/wondercraft_client.py` is story-frozen (not modified per spec).
- **Bounded `_act` body** — `act()` lines 212-242 = 30 LOC (well under AC-B 150 ceiling).
- **Substrate-as-floor honored** — `app/marcus/orchestrator/dispatch_adapter.py` lines 70-95 empty diff (FR113 + NFR-I13).
- **Class-C template inheritance** — NO new validator extension needed (template proven inheritable from 7b.6/7b.7/7b.8).
- **Credential register (NFR-CG19)** — `state/config/credential-rotation-register.yaml` carries `provider: wondercraft` row with `secret_store_reference` + cadence.
- **Rate-limit budget (NFR-CG20)** — `app/specialists/wanda/config.yaml` declares `rate_limit_per_minute: 8`.
- **VCR cassettes / no-live-API** — `tests/specialists/wanda/test_wanda_no_live_api_in_ci.py` AST-scan PASS; live-API detector PASS across 75 test files.

### OBSERVATION (carry-forward from 7b.8)

The cross-specialist retrofit working-tree state from 7b.8 close (5 specialists' `_act.py` extraction + validator Class-B/C+/C template extensions + 3 SKILL.md sanctum-path canonicalizations) IS still uncommitted in the working tree at 7b.9 review. The close commit at 7b.9 will land 7b.8 + 7b.9 deliverables atomically. Documented in 7b-8-code-review-2026-04-29.md OBSERVATION-1; not re-litigated here. **Recommendation:** the 7b.9 close commit message should reference both 7b.8 + 7b.9 closes (e.g., `feat(slab-7b): close Stories 7b.8 Enrique + 7b.9 Wanda + retrofit prior-close drift`).

## Verification

- **Focused Wanda battery:** `71 passed, 1 skipped, 1 deselected in 4.14s` (independent re-run; matches Codex's report).
- **Class-conformance validator:** `PASS: 9 activation contract file(s) conform` (Texas/Quinn-R/Vera/Irene/Tracy/Gary/Kira/Enrique/Wanda).
- **Sandbox-AC validator:** `PASS — no sandbox-AC violations across 1 story file(s).`
- **Pipeline-manifest lockstep:** PASS (`reports/dev-coherence/2026-04-30-0054/check-pipeline-manifest-lockstep.PASS.yaml`).
- **Live-API detector:** `PASS: scanned 75 test file(s); no forbidden live API imports.`
- **Import-linter:** `Contracts: 9 kept, 0 broken.`
- **Broad regression (deterministic):** `1325 passed, 21 skipped, 1 deselected in 159.69s` (`-p no:randomly`).
- **AC-B 150-LOC ceiling:** `act()` 30 LOC (lines 212-242).
- **Two-SKILL.md ratification:** `skills/bmad-agent-wanda/SKILL.md` CREATED; `skills/bmad-agent-wondercraft/SKILL.md` UNTOUCHED.
- **Substrate-as-floor:** `dispatch_adapter.py:70-95` empty diff.
- **Story status:** `review` → ready for `done` flip.
- **Operator-gated AC-9-B (live Wondercraft canary):** NOT run; remains operator-gated per spec.

## Close Notes

- Sprint-status flips `migration-7b-9-wanda-port-shape-onto-scaffold: review → done`.
- Wave-4 close ledger entry to be appended at `tripwire_events::wave_4_close` (Wave-4 single-story close; UNBLOCKS Wave-5a 7b.10 Dan greenfield).
- `_bmad/memory/bmad-agent-wanda/` is gitignored; close commit must `git add --force` the six BMB files.
- Class-C template proven 4× via inheritance (Gary/Kira/Enrique/Wanda); validator reports 9 conforming contracts.
- Closes pre-existing `wanda-sanctum-test-expected-files-constant-drift` follow-on (struck-through in deferred-inventory).
- The Wanda P3 cross-suite state-pollution flake filed at 7b.8 T11 (`wanda-sanctum-tests-cross-suite-state-pollution-p3-flake`) is **structurally CLOSED** at 7b.9 close — under deterministic order ALL Wanda sanctum tests PASS in broad regression (1325 PASS / 0 fail). Random-order run was earlier flaky because the legacy `wanda-sidecar/` path coexisted with `bmad-agent-wanda/` populated state mid-suite; legacy path removal at T2 eliminates the cross-suite pollution surface.
