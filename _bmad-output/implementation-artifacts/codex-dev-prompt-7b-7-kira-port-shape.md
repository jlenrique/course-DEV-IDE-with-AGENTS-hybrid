# Codex dev-story prompt — Story 7b.7 Kira Port-Shape (Slab 7b Wave-3 parallel)

**Cycle:** Claude spec → Codex dev+tests → Claude bmad-code-review + commit + flip done.
**Wave:** 3 parallel — PARALLEL with 7b.6 Gary (already in review/done) + 7b.8 Enrique. Opens once 7b.6 reaches `done` so the wave_3_first_port_tripwire ledger entry is readable.
**Gate:** **single (DEFAULT) → dual (CONDITIONAL via Round-(e) E3 binding-hard `conditional_gate_override` keyed to 7b.6 first-port tripwire)**.
**Class:** C API-bound (Kling API; third-party).
**No k_contract block on 7b-7 itself** (gate-mode is resolved at story-open per E3, NOT at close per E6).

**Round-(e) E3 binding-hard — gate-mode resolution at story-open:** Sprint runner MUST read `sprint-status.yaml::tripwire_events::wave_3_first_port_tripwire::fired_verdict` at 7b.7 story-open. If `fired_verdict: true` (7b.6 closed >2.7K LOC), 7b.7 OPENS DUAL-GATE (binding=hard; sprint runner enforces). If `fired_verdict: false`, 7b.7 OPENS SINGLE-GATE (default).

**STATUS:** Spec READY-FOR-DEV at `_bmad-output/implementation-artifacts/migration-7b-7-kira-port-shape.md` (Claude-authored 2026-04-29; sandbox-AC validator PASS; 14 ACs A-N + 11 task blocks).

**Class-C two-SKILL.md convention RATIFIED 2026-04-29 by party-mode 4/4 unanimous (John+Mary+Amelia+Murat) on option (a):**
- **Create NEW persona-skill at `skills/bmad-agent-kira/SKILL.md`** with minimal FR101 R1-compliant frontmatter (only `name: bmad-agent-kira` + `description`); body = activation hot-load batch referencing `_bmad/memory/bmad-agent-kira/` BMB sanctum
- **PRESERVE existing `skills/bmad-agent-kling/SKILL.md`** UNTOUCHED — Slab 2b.x era Kling API-mastery skill with rich content; consume lazily as API reference; activation order in NEW kira/SKILL.md says "Use `skills/bmad-agent-kling/` only as Kling API reference material"
- This mirrors 7b.6 Gary's pattern (persona at `bmad-agent-gary/`, API-mastery at `bmad-agent-gamma/`); test result: 18/18 SG-4 cross-specialist parity tests PASS post-7b.6 close
- The operator-decision gate from earlier prompt-draft is RESCINDED; no decision needed at T1.

---

```
Run bmad-dev-story on Story 7b.7 (Slab 7b Wave-3 parallel; Class-C API-bound; gate-mode-RESOLVED-at-story-open per Round-(e) E3 conditional_gate_override; Kling API live invocation + motion generation per motion_plan.yaml + per-slide .progress.json + terminal .json receipts + reviewer inspection pack + fail-closed budget rules).

## Required reading (read in order)

1. **Story spec:** `_bmad-output/implementation-artifacts/migration-7b-7-kira-port-shape.md` (status: ready-for-dev; 14 ACs A-N; 11 tasks; you own T1-T10; Claude owns T11 close).
2. **Round-(e) governance JSON** — `docs/dev-guide/migration-story-governance.json` §`stories.7b-7.conditional_gate_override` (trigger_story=7b-6; binding=hard).
3. **Wave-3 first-port close-verdict** — read `sprint-status.yaml::tripwire_events::wave_3_first_port_tripwire`. **HARD CHECKPOINT:** If 7b.6 not yet at `done` status OR ledger entry absent → HALT until close lands.
4. **7b.6 Gary precedent (Class-C TEMPLATE)** — `_bmad-output/implementation-artifacts/migration-7b-6-gary-port-shape.md` + `_bmad-output/implementation-artifacts/7b-6-code-review-2026-04-XX.md`. Inherit: Class-C template (validator), 6-file BMB sanctum at `bmad-agent-{specialist}/`, VCR cassettes, NFR-CG13/19/20, operator-gated AC-N-B canary.
5. **Class-C two-SKILL.md convention RATIFIED (party-mode 4/4 unanimous 2026-04-29; binding for 7b.7):** Kira creates NEW persona-skill at `skills/bmad-agent-kira/SKILL.md` (specialist-name path; minimal FR101 R1 frontmatter); PRESERVES existing `skills/bmad-agent-kling/SKILL.md` (API-mastery; consume only; NOT modified). Mirrors 7b.6 Gary pattern. NO operator-decision gate; convention is binding.
6. **PRD §FR95** — `_bmad-output/planning-artifacts/prd-slab-7b-specialist-activation-eleven.md` §FR95. Kling API + motion generation + per-slide progress + terminal receipts + reviewer inspection pack + fail-closed budgets.
7. **Sandbox-AC inventory entry `kling` (FR107; Wave 0 LANDED)** — `docs/dev-guide/migration-ac-sandbox-inventory.json` §`kling`.
8. **Slab 2b.1 TEMPLATE** — `_bmad-output/implementation-artifacts/migration-2b-1-gary-scaffold-migration.md`.
9. **Specialist migration template (R1-R14)** — `docs/dev-guide/specialist-migration-template.md`.
10. **`scripts/api_clients/kling_client.py` + `scripts/api_clients/kling_public_client.py`** — Kling API client (already shipped).

## T1 hard checkpoints (HALT-AND-SURFACE if violated)

- Round-(e) E3 trigger-story binding verified.
- **7b.6 Gary status `done` in sprint-status.yaml** (NOT just `review` — need full close-verdict in tripwire ledger).
- `wave_3_first_port_tripwire` ledger entry EXISTS at `sprint-status.yaml::tripwire_events`.
- Gate-mode resolved per `fired_verdict`: single (false) or dual (true).
- Wave-1 + Wave-2a + Wave-2b + Wave-3-first-port (7b.6) all closed.
- Class-C template active in validator from 7b.6 close (verified via `validate_parity_test_class_conformance.py tests/parity/` PASS — should show 6 activation contracts post-7b.6 close).
- Kira baseline at `app/specialists/kira/`: `__init__.py expertise/ kling_dispatch.py graph.py model_config.yaml state.py` (Slab 2b era; Kling dispatch present).
- `_bmad/memory/bmad-agent-kira/` does NOT yet exist (sanctum greenfield; this story creates 6-file BMB).
- `skills/bmad-agent-kling/SKILL.md` exists (verified: yes per epic line 764 canonical reference).
- (REMOVED — operator-decision gate on SKILL.md convention rescinded; party-mode ratified two-SKILL.md as canonical Class-C 2026-04-29)
- `scripts/api_clients/kling_client.py` exists.
- FR107 sandbox-AC `kling` entry present.
- Sandbox-AC validator pre-flight PASS.

## Files in scope

**New (≥9 files; +1 if two-SKILL.md pattern adopted):**
- `_bmad/memory/bmad-agent-kira/INDEX.md` + `PERSONA.md` + `CREED.md` + `BOND.md` + `MEMORY.md` + `CAPABILITIES.md` — 6-file BMB sanctum (Class-C; specialist-name path)
- `tests/parity/test_kira_activation_contract.py` — flat layout; Class-C template (`class_template_id = "C"`)
- `tests/specialists/kira/test_kira_motion_generation.py` — VCR cassette; per-slide .progress.json + terminal .json receipts
- `tests/specialists/kira/test_kira_fail_closed_budget.py` — VCR cassette with synthetic budget-exhaust; clean abort
- `tests/specialists/kira/test_kira_no_live_api_in_ci.py` — AST-scan
- `tests/specialists/kira/test_kira_summary_landing.py` — 7a.5 facade
- `tests/composition/test_kira_to_compositor_chain.py` — fixture-replay until 7b.11 lands
- `tests/fixtures/specialist-replay/kira/*.yaml` — VCR cassettes
- `_bmad-output/implementation-artifacts/7b-7-codex-self-review-2026-04-XX.md` — T10 G6 self-review
- `skills/bmad-agent-kira/SKILL.md` — NEW persona-skill (Class-C two-SKILL.md convention; minimal FR101 R1 frontmatter `name: bmad-agent-kira` + persona-focused description; body = activation hot-load batch referencing `_bmad/memory/bmad-agent-kira/` BMB sanctum + line documenting that `skills/bmad-agent-kling/` is API-mastery reference material consumed lazily)

**Modified:**
- `app/specialists/kira/_act.py` — refine bounded body; ≤150 LOC AC-B ceiling; invoke `kling_client.py`
- `app/specialists/kira/graph.py` — additive delegation (mirror Texas/Quinn-R/Vera/Irene-Pass-1/Tracy/Gary precedent)
- `app/specialists/kira/config.yaml` — NEW or EXTENDED (rate-limit budget per NFR-CG20)
- (REMOVED — `skills/bmad-agent-kling/SKILL.md` is PRESERVED untouched per two-SKILL.md ratification; Slab 2b.x API-mastery content stays intact)
- `state/config/credential-rotation-register.yaml` — ADD Kling API row
- (NO `validate_parity_test_class_conformance.py` extension — Class-C template inherited from 7b.6 without modification)

**Do NOT modify:**
- `app/marcus/orchestrator/dispatch_adapter.py` lines 70-95 (substrate-frozen)
- 7b.1-7b.6 substrate (consume only)
- Legacy `kling_dispatch.py` semantics (consume as helper)
- `scripts/api_clients/kling_client.py` (the API client; consume only)
- Class-C template assertions in validator (inherited from 7b.6 unchanged)

## Critical implementation notes

- **9-node scaffold per Slab 2b.1 TEMPLATE:** Kira baseline already has scaffold from Slab 2b era; refine `_act` body, KEEP scaffold.
- **Conditional gate-mode at story-open (Round-(e) E3 binding-hard):** record resolved gate mode in T1.6 Drift Resolution + Dev Agent Record. If dual-gate, additional T11 close items: operator-witnessed dual-gate ceremony (mirrors 7a-8 precedent).
- **Class-C template inherited from 7b.6 (NO new template extension):** the validator already supports Class-C; Kira's parity test passes with `class_template_id = "C"`. No lockstep validator extension this story.
- **Motion generation per `motion_plan.yaml`:** Kira reads motion_plan from envelope payload; generates motion per slide; emits per-slide `.progress.json` (intermediate) + terminal `.json` receipts (final; success/failure with cost-tracking).
- **Reviewer inspection pack at `[BUNDLE_PATH]/recovery/inspection/`:** one folder per failed slide with operator-readable forensics.
- **Fail-closed budget rules (NFR-CG20):** budget exceeded → clean abort with terminal receipt `status: budget-exceeded`; subsequent slides NOT attempted; failure path emits to `recovery/inspection/<slide_id>/budget-exhausted.md`.
- **AC-B 150-LOC ceiling on `_act` body.**
- **Live-API discipline (NFR-CG13 strict):** All Kira tests use VCR cassettes under `tests/fixtures/specialist-replay/kira/`. Live canary belongs ONLY in operator-gated AC-7-B Completion-Notes block.
- **Cache-hit-rate N/A for Class-C:** Kira is REST-API tool-dispatch (no LLM at Kira layer; same as Gary).
- **Credential register (NFR-CG19):** ADD Kling row at `state/config/credential-rotation-register.yaml`.
- **Rate-limit budget (NFR-CG20):** declare in `app/specialists/kira/config.yaml`.
- **PyYAML, NOT ruamel.** No new third-party deps. Sanctum gitignored — Claude T11 commit uses `git add --force`.

## Verification battery (T9)

```bash
.venv/Scripts/python.exe -m pytest tests/parity/test_kira_activation_contract.py tests/specialists/kira tests/composition/test_kira_to_compositor_chain.py tests/parity/test_skill_md_sanctum_alignment.py -q --tb=short
.venv/Scripts/python.exe -m pytest tests/unit/manifest tests/integration/marcus tests/composition tests/parity tests/structural tests/unit/marcus tests/specialists tests/cli tests/unit/models -q --tb=line --ignore=tests/integration/marcus/test_directive_confirm_or_edit_prompt.py
.venv/Scripts/python.exe scripts/utilities/check_pipeline_manifest_lockstep.py
.venv/Scripts/python.exe scripts/utilities/detect_live_api_in_tests.py
.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7b-7-kira-port-shape.md
.venv/Scripts/python.exe scripts/utilities/validate_parity_test_class_conformance.py tests/parity/
.venv/Scripts/python.exe -m ruff check app/specialists/kira tests/parity/test_kira_activation_contract.py tests/specialists/kira tests/composition/test_kira_to_compositor_chain.py
.venv/Scripts/lint-imports.exe
```

Expected: zero new failures vs post-7b.6 baseline (pre-existing Wanda flake + Desmond out-of-scope flake remain).

## T10 + T11

- **T10 (Codex):** G6 self-review at `_bmad-output/implementation-artifacts/7b-7-codex-self-review-2026-04-XX.md`. Flip status `in-progress → review`.
- **T11 (Claude):** bmad-code-review at `7b-7-code-review-2026-04-XX.md`; remediation cycle 1 if PASS-WITH-PATCH; operator-gated AC-7-B if window opens; **append wave_3_parallel_close ledger entry with 7b.7 contribution** (separate from wave_3_first_port_tripwire from 7b.6); sprint-status flip done; commit + push (force-add gitignored sanctum); next-session-start-here.md pivot to 7b.8 Enrique close + 7b.9 Wanda Wave-4 open.

## Boundary

**HALT-AND-SURFACE on:**
- (a) 7b.6 not at `done` (need close-verdict in ledger before this story can resolve gate-mode)
- (b) `wave_3_first_port_tripwire` ledger entry absent
- (c) Round-(e) E3 binding-hard pin mismatch
- (d) AC-B 150-LOC ceiling exceeded
- (e) substrate-frozen-paths violation
- (f) sandbox-AC violation
- (g) live-API import detected by AST scan in CI test files
- (h) sanctum 6-file BMB pattern drift from Class-A precedent (must match 6-file pattern)
- (i) Class-C template inheritance breaks (validator must PASS without modification)
- (j) credential register + rate-limit budget entries missing (NFR-CG19/CG20)
- (k) **OPERATOR DECISION on SKILL.md convention (single vs two-SKILL.md) NOT recorded** — surface to operator at T1 if not pre-resolved

**Do NOT:**
- Touch substrate-frozen lines
- Modify legacy `kling_dispatch.py` semantics (consume as helper)
- Modify `scripts/api_clients/kling_client.py` (consume only)
- Modify 7b.1-7b.6 substrate (parity base, chain base, validator A/B/C+/C templates, prior story scaffolds)
- Extend Class-C template assertions in validator (inherited from 7b.6 without modification)
- Introduce ruamel.yaml or new third-party deps
- Author `tests/parity/per_specialist/` subdir (Errata 4 verdict-flat)
- Run live Kling API in CI (NFR-CG13 strict)
```
