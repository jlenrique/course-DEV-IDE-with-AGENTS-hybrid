# Codex dev-story prompt — Story 7b.9 Wanda Port-Shape Onto Scaffold (Slab 7b Wave-4)

**Cycle:** Claude spec → Codex dev+tests → Claude bmad-code-review + commit + flip done.
**Wave:** 4 — strict-after-Wave-3 (7b.6 + 7b.7 + 7b.8 all `done`) per epic Story 7b.9 line 845; OR parallelizable with Wave-3 tail per operator preference.
**Gate:** **SINGLE-GATE** (per Round-(e) governance JSON `7b-9`; no conditional gate-mode binding).
**Class:** C API-bound (Wondercraft API; third-party).

**Class-C two-SKILL.md convention RATIFIED 2026-04-29 (party-mode 4/4 unanimous on option (a); binding for 7b.9):**
- **CREATE NEW persona-skill at `skills/bmad-agent-wanda/SKILL.md`** with minimal FR101 R1-compliant frontmatter (`name: bmad-agent-wanda` + persona-focused description); body = activation hot-load batch referencing `_bmad/memory/bmad-agent-wanda/` BMB sanctum + line documenting "Use `skills/bmad-agent-wondercraft/` only as Wondercraft API reference material; runtime execution via `app/specialists/wanda/`."
- **PRESERVE** `skills/bmad-agent-wondercraft/SKILL.md` UNTOUCHED — Slab 2b.x era Wondercraft API-mastery skill; consume lazily as API reference; NOT modified by this story.
- Mirrors 7b.6 Gary + 7b.7 Kira + 7b.8 Enrique pattern (4th application; Class-C inheritance proven).

**Note: Wanda has THREE drifts surfacing at T1 (NOT just one):**
1. **Drift #1 — Sanctum migration:** existing `_bmad/memory/bmad-agent-wanda/` is partial 5+1-sidecar pattern (CLONE-FORK-NOTICE/INDEX/PERSONA/access-boundaries/chronology + L6-operational/) from Slab 2c.1 era. MUST migrate to canonical 6-file BMB (INDEX/PERSONA/CREED/BOND/MEMORY/CAPABILITIES). Closes pre-existing flake `wanda-sanctum-test-expected-files-constant-drift` follow-on.
2. **Drift #2 — Class-C two-SKILL.md ratified-binding:** create persona at `bmad-agent-wanda/`; preserve API-mastery at `bmad-agent-wondercraft/`.
3. **Drift #3 — scaffold-v0.2 alignment gap:** Wanda's `app/specialists/wanda/graph.py` was developed in Slab 2c.1 BEFORE the 9-node scaffold canonical was finalized; this story aligns existing scaffold to canonical `SCAFFOLD_NODE_IDS` per FR96.

**STATUS:** Spec READY-FOR-DEV at `_bmad-output/implementation-artifacts/migration-7b-9-wanda-port-shape-onto-scaffold.md` (Claude-authored 2026-04-29; sandbox-AC validator PASS; 16 ACs A-P + 12 task blocks T1-T12; 3 drifts amended at T1.6).

---

```
Run bmad-dev-story on Story 7b.9 (Slab 7b Wave-4; Class-C API-bound; SINGLE-GATE per governance JSON; Wondercraft API live invocation + podcast/audio bed generation scoped into storyboard's audio track + scaffold-v0.2 alignment).

## Required reading (read in order)

1. **Story spec:** `_bmad-output/implementation-artifacts/migration-7b-9-wanda-port-shape-onto-scaffold.md` (status: ready-for-dev; 16 ACs A-P; 12 tasks; you own T1-T10; Claude owns T11 close).
2. **Round-(e) governance JSON** — `docs/dev-guide/migration-story-governance.json` §`stories.7b-9` (single-gate; expected_pts=4; expected_k_target=1.4; no conditional binding; no k_contract).
3. **Wave-3 close-state** — read `sprint-status.yaml::tripwire_events::wave_3_first_port_tripwire` (verified `fired_verdict: false`) + 7b.6/7b.7/7b.8 statuses (all should be `done` before 7b.9 opens; if 7b.8 still `review`, HALT — Wave-3 close incomplete).
4. **7b.6/7b.7/7b.8 Class-C precedents (Wave-3 inheritance)** — Gary + Kira + Enrique. Inherit Class-C template (validator), 6-file BMB sanctum at `bmad-agent-{specialist}/`, two-SKILL.md ratified-binding, VCR cassettes, NFR-CG13/19/20, operator-gated AC-N-B canary. Wanda is the 4TH Class-C application — template fully proven.
5. **PRD §FR96** — `_bmad-output/planning-artifacts/prd-slab-7b-specialist-activation-eleven.md` §FR96. Wondercraft API live invocation + podcast/audio bed generation scoped into storyboard's audio track + scaffold-v0.2 alignment (closes pre-Slab-2b client-landed-not-on-scaffold gap).
6. **Sandbox-AC inventory entry `wondercraft` (FR107; Wave 0 LANDED)** — `docs/dev-guide/migration-ac-sandbox-inventory.json` §`wondercraft`.
7. **Slab 2b.1 TEMPLATE precedent** — `_bmad-output/implementation-artifacts/migration-2b-1-gary-scaffold-migration.md`.
8. **Pre-existing Wanda sanctum flake** — `tests/specialists/wanda/test_wanda_sanctum_populated.py::test_sanctum_digest_nonempty_post_population` fails on `EXPECTED_SANCTUM_FILES` constant drift (5 expected vs 6 actual). Already filed as `wanda-sanctum-test-expected-files-constant-drift` follow-on. **THIS STORY CLOSES IT** via sanctum-migration to 6-file BMB pattern + parity-test target update at T2.
9. **`scripts/api_clients/wondercraft_client.py`** — Wondercraft API client (already shipped; Slab 2c.1 era).
10. **CLAUDE.md** — §LangChain/LangGraph migration governance + NFR-CG13/19/20 + bmad-memory-gitignore-force-add-policy.

## T1 hard checkpoints (HALT-AND-SURFACE if violated)

- Round-(e) governance pin verified (`d['version'] == '2026-04-29-slab7b-twelve-stories'`; `d['stories']['7b-9']['expected_gate_mode'] == 'single-gate'`).
- 7b.6 + 7b.7 + 7b.8 statuses all `done` in sprint-status.yaml (Wave-3 close complete).
- Class-C template active in validator from 7b.6 close (verified via `validate_parity_test_class_conformance.py tests/parity/` PASS — should show 9+ activation contracts post-Wave-3 close).
- Wanda baseline at `app/specialists/wanda/`: `__init__.py expertise/ graph.py model_config.yaml state.py wondercraft_dispatch.py` (Slab 2c.1 era; client-landed-not-on-scaffold).
- `_bmad/memory/bmad-agent-wanda/` EXISTS PARTIAL (5-file sidecar pattern + L6-operational/; this story migrates to 6-file BMB).
- `skills/bmad-agent-wondercraft/` exists (Slab 2b.x API-mastery; PRESERVED untouched).
- `skills/bmad-agent-wanda/` does NOT yet exist (this story creates per two-SKILL.md ratification).
- `scripts/api_clients/wondercraft_client.py` exists.
- FR107 sandbox-AC `wondercraft` entry present.
- Sandbox-AC validator pre-flight PASS.

## Files in scope

**New / Migrated (≥10 files):**
- `_bmad/memory/bmad-agent-wanda/INDEX.md` (refresh existing) + `PERSONA.md` (refresh existing) + `CREED.md` (NEW; operating principles per BMB checklist) + `BOND.md` (rename from `access-boundaries.md`; preserve content) + `MEMORY.md` (rename from `chronology.md`; preserve content) + `CAPABILITIES.md` (NEW; consume from `skills/bmad-agent-wondercraft/references/`) — canonical 6-file BMB
- DELETE legacy: `_bmad/memory/bmad-agent-wanda/CLONE-FORK-NOTICE.md` + `_bmad/memory/bmad-agent-wanda/L6-operational/` (preserve content out-of-band if operator requests)
- `skills/bmad-agent-wanda/SKILL.md` — NEW persona-skill (Class-C two-SKILL.md convention)
- `tests/parity/test_wanda_activation_contract.py` — flat layout; Class-C template (`class_template_id = "C"`; `specialist_name = "wanda"`)
- `tests/specialists/wanda/test_wanda_audio_bed_generation.py` — VCR cassette; podcast/audio bed generation scoped into storyboard's audio track
- `tests/specialists/wanda/test_wanda_no_live_api_in_ci.py` — AST-scan
- `tests/specialists/wanda/test_wanda_summary_landing.py` — 7a.5 facade integration
- `tests/composition/test_wanda_to_compositor_chain.py` — fixture-replay until 7b.11 lands
- `tests/fixtures/specialist-replay/wanda/*.yaml` — VCR cassettes
- `_bmad-output/implementation-artifacts/7b-9-codex-self-review-2026-04-XX.md` — T10 G6 self-review

**Modified:**
- `app/specialists/wanda/_act.py` — refine bounded body; ≤150 LOC AC-B ceiling; invoke `wondercraft_client.py`
- `app/specialists/wanda/graph.py` — **scaffold-v0.2 alignment** to canonical `SCAFFOLD_NODE_IDS` per FR96 (Drift #3 resolution)
- `app/specialists/wanda/config.yaml` — NEW or EXTENDED (rate-limit budget per NFR-CG20)
- `tests/specialists/wanda/test_wanda_sanctum_populated.py::EXPECTED_SANCTUM_FILES` — UPDATE constant from 5-file tuple to canonical 6-file BMB tuple (closes flake at T2.3)
- `state/config/credential-rotation-register.yaml` — ADD Wondercraft API row
- `_bmad-output/planning-artifacts/deferred-inventory.md` — close `wanda-sanctum-test-expected-files-constant-drift` follow-on at T2.5
- (NO `validate_parity_test_class_conformance.py` extension — Class-C template inherited from 7b.6 unchanged)

**Do NOT modify:**
- `app/marcus/orchestrator/dispatch_adapter.py` lines 70-95 (substrate-frozen).
- 7b.1-7b.8 substrate (consume only).
- `skills/bmad-agent-wondercraft/SKILL.md` (PRESERVED untouched per two-SKILL.md ratification; Slab 2b.x API-mastery content stays intact).
- Legacy `wondercraft_dispatch.py` semantics (consume as helper).
- `scripts/api_clients/wondercraft_client.py` (the API client; consume only).
- Class-C template assertions in validator (inherited from 7b.6 unchanged).

## Critical implementation notes

- **9-node scaffold-v0.2 alignment (FR96 primary; Drift #3):** Wanda's existing `graph.py` was Slab 2c.1 pre-canonical-scaffold; align nodes to canonical `SCAFFOLD_NODE_IDS = (receive, plan, act, verify, reflect, emit_spans, gate_decision, finalize, handoff)` per `tests/integration/scaffold_conformance/scaffold_contract.py`. Closes the pre-Slab-2b client-landed-not-on-scaffold gap.
- **Two-SKILL.md ratified-binding (Drift #2):** CREATE `skills/bmad-agent-wanda/SKILL.md` (persona); PRESERVE `skills/bmad-agent-wondercraft/SKILL.md` (API-mastery). 4th application of pattern.
- **Sanctum migration to 6-file BMB (Drift #1):** translate 5+1-sidecar to canonical 6-file. KEEP existing INDEX/PERSONA content (refresh per BMB checklist); RENAME `chronology.md`→`MEMORY.md` (preserve content); RENAME `access-boundaries.md`→`BOND.md` (preserve content); ADD `CREED.md` (NEW; operating principles); ADD `CAPABILITIES.md` (NEW; consume Wondercraft API capabilities from `skills/bmad-agent-wondercraft/references/`); DELETE `CLONE-FORK-NOTICE.md` + `L6-operational/`.
- **`wanda-sanctum-test-expected-files-constant-drift` flake closure:** at T2.3, update `tests/specialists/wanda/test_wanda_sanctum_populated.py::EXPECTED_SANCTUM_FILES` constant to canonical 6-file BMB tuple. Verify `test_sanctum_digest_nonempty_post_population` PASSES post-migration. At T2.5, close the deferred-inventory follow-on.
- **Class-C template inherited from 7b.6 (NO new template extension):** validator already supports Class-C; Wanda parity test passes with `class_template_id = "C"`. NO lockstep validator extension.
- **Podcast/audio bed generation (FR96 primary):** Wanda emits podcast/audio bed audio at `[BUNDLE_PATH]/assembly-bundle/audio/beds/<bed_id>.{mp3|wav}`; scoped into storyboard's audio track per Pass-2 narration manifest. Wondercraft API generates beds based on storyboard mood/genre cues.
- **AC-B 150-LOC ceiling on `_act` body.**
- **Live-API discipline (NFR-CG13 strict):** All Wanda tests use VCR cassettes under `tests/fixtures/specialist-replay/wanda/`. Live canary belongs ONLY in operator-gated AC-9-B Completion-Notes block.
- **Cache-hit-rate N/A for Class-C:** Wanda is REST-API tool-dispatch (no LLM at Wanda layer; same as Gary/Kira/Enrique).
- **Credential register (NFR-CG19):** ADD Wondercraft row at `state/config/credential-rotation-register.yaml`.
- **Rate-limit budget (NFR-CG20):** declare in `app/specialists/wanda/config.yaml`.
- **PyYAML, NOT ruamel.** No new third-party deps. Sanctum gitignored — Claude T11 commit uses `git add --force` for `_bmad/memory/bmad-agent-wanda/`.

## Verification battery (T9)

```bash
.venv/Scripts/python.exe -m pytest tests/parity/test_wanda_activation_contract.py tests/specialists/wanda tests/composition/test_wanda_to_compositor_chain.py tests/parity/test_skill_md_sanctum_alignment.py -q --tb=short
.venv/Scripts/python.exe -m pytest tests/unit/manifest tests/integration/marcus tests/composition tests/parity tests/structural tests/unit/marcus tests/specialists tests/cli tests/unit/models -q --tb=line --ignore=tests/integration/marcus/test_directive_confirm_or_edit_prompt.py
.venv/Scripts/python.exe scripts/utilities/check_pipeline_manifest_lockstep.py
.venv/Scripts/python.exe scripts/utilities/detect_live_api_in_tests.py
.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7b-9-wanda-port-shape-onto-scaffold.md
.venv/Scripts/python.exe scripts/utilities/validate_parity_test_class_conformance.py tests/parity/
.venv/Scripts/python.exe -m ruff check app/specialists/wanda tests/parity/test_wanda_activation_contract.py tests/specialists/wanda tests/composition/test_wanda_to_compositor_chain.py
.venv/Scripts/lint-imports.exe
```

Expected: zero new failures vs post-7b.8 baseline. **`test_wanda_sanctum_populated.py::test_sanctum_digest_nonempty_post_population` MUST flip from FAIL → PASS as part of this story (Drift #1 + flake closure).**

## T10 + T11

- **T10 (Codex):** G6 self-review at `_bmad-output/implementation-artifacts/7b-9-codex-self-review-2026-04-XX.md`. Flip status `in-progress → review`.
- **T11 (Claude):** bmad-code-review at `7b-9-code-review-2026-04-XX.md`; remediation cycle 1 if PASS-WITH-PATCH; operator-gated AC-9-B if window opens; **append `wave_4_close` ledger entry** (Wave-4 single-story close) to `sprint-status.yaml::tripwire_events`; close `wanda-sanctum-test-expected-files-constant-drift` follow-on; sprint-status flip done; commit + push (force-add gitignored sanctum); next-session-start-here.md pivot to 7b.10 Wave-5a Dan greenfield open.

## Boundary

**HALT-AND-SURFACE on:**
- (a) 7b.6/7b.7/7b.8 not all `done` in sprint-status (Wave-3 close incomplete) — strict prereq
- (b) `wave_3_first_port_tripwire` ledger entry absent or `fired_verdict` not `false` (Class-C template may be in unstable state)
- (c) Round-(e) governance pin mismatch
- (d) AC-B 150-LOC ceiling exceeded
- (e) substrate-frozen-paths violation
- (f) sandbox-AC violation
- (g) live-API import detected by AST scan in CI test files
- (h) sanctum 6-file BMB pattern drift from canonical (must match `INDEX/PERSONA/CREED/BOND/MEMORY/CAPABILITIES` exactly)
- (i) Class-C template inheritance breaks (validator must PASS without modification)
- (j) credential register + rate-limit budget entries missing (NFR-CG19/CG20)
- (k) two-SKILL.md ratified-binding violated (must CREATE `skills/bmad-agent-wanda/SKILL.md` AND must NOT modify `skills/bmad-agent-wondercraft/SKILL.md`)
- (l) `EXPECTED_SANCTUM_FILES` constant not updated to 6-file BMB tuple (flake remains open)
- (m) scaffold-v0.2 alignment gap not closed (Drift #3; `graph.py` must conform to canonical `SCAFFOLD_NODE_IDS`)

**Do NOT:**
- Touch substrate-frozen lines
- Modify legacy `wondercraft_dispatch.py` semantics (consume as helper)
- Modify `scripts/api_clients/wondercraft_client.py` (consume only)
- Modify 7b.1-7b.8 substrate (parity base, chain base, validator A/B/C+/C templates, prior story scaffolds)
- Extend Class-C template assertions in validator (inherited from 7b.6 without modification)
- Modify `skills/bmad-agent-wondercraft/SKILL.md` (PRESERVED per two-SKILL.md ratification)
- Introduce ruamel.yaml or new third-party deps
- Author `tests/parity/per_specialist/` subdir (Errata 4 verdict-flat)
- Run live Wondercraft API in CI (NFR-CG13 strict)
- Skip the 6-file BMB sanctum migration (Drift #1 closure is non-negotiable)
- Skip the scaffold-v0.2 alignment refactor (Drift #3 closure is non-negotiable per FR96)
- Leave `CLONE-FORK-NOTICE.md` or `L6-operational/` in the sanctum (legacy artifacts; preserve content out-of-band if needed)
```
