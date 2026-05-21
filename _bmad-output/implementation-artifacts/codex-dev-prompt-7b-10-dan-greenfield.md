# Codex dev-story prompt — Story 7b.10 Dan Greenfield (Slab 7b Wave-5a)

**Cycle:** Claude spec → Codex dev+tests → Claude bmad-code-review + commit + flip done.
**Wave:** 5a — strict-after-Wave-4 (7b.9 Wanda `done`).
**Gate:** **SINGLE-GATE** (per Round-(e) governance JSON `7b-10`; k_contract tripwire 4.0K).
**Class:** D1 LLM-greenfield (default LLM-only resolution; conditional third-party-API path is party-mode-gated per B1/C1 binding).

**T1 BLOCKING DECISION — `dan-api-tbd-pending` resolution:**
- **DEFAULT (LLM-only):** Dan is a creative-director aux specialist contributing prose at G1/G1A/G2; LLM-only invocation through shared LLM facade; sandbox-AC inventory entry `dan-api-tbd-pending` is RETIRED in lockstep with T2 commit.
- **ALTERNATIVE (third-party-API):** if T1 surfaces a design-mandated provider constraint (none known per PRD §FR98), HALT-AND-SURFACE per Round-(b) Mary B1 + Round-(c) C1 binding-hard. Dev-agent does NOT unilaterally promote — operator must convene party-mode + governance-JSON version bump BEFORE T3 opens.

**Class-D1 introduces NEW template extension to validator (LOCKSTEP foundational deliverable):**
- This is the FIRST Slab 7b D1 greenfield. Class-D1 template assertions added to `scripts/utilities/validate_parity_test_class_conformance.py` in this story.
- After 7b.10 close, validator supports A/B/C+/C/D1 (5 classes; D2 added by 7b.11; integration aggregated by 7b.12).

**STATUS:** Spec READY-FOR-DEV at `_bmad-output/implementation-artifacts/migration-7b-10-dan-greenfield.md` (Claude-authored 2026-04-29; sandbox-AC validator PASS; 12 ACs A-L + 12 task blocks T1-T12; k_contract tripwire 4.0K binding).

---

```
Run bmad-dev-story on Story 7b.10 (Slab 7b Wave-5a; Class-D1 LLM-greenfield; SINGLE-GATE per governance JSON; bmad-create-specialist invocation; SKILL.md option-a sanctum-aligned + 6-file BMB sidecar + app/specialists/dan/ scaffold-v0.2 instantiation + _act narrow-lane creative-director aux contributions G1-G2).

## Required reading (read in order)

1. **Story spec:** `_bmad-output/implementation-artifacts/migration-7b-10-dan-greenfield.md` (status: ready-for-dev; 12 ACs A-L; 12 tasks; you own T1-T10; Claude owns T11 close).
2. **Round-(e) governance JSON** — `docs/dev-guide/migration-story-governance.json` §`stories.7b-10` (single-gate; expected_pts=4; expected_k_target=1.5; k_contract tripwire 4.0K; B1/C1 binding-hard).
3. **Wave-4 close-state** — read `sprint-status.yaml::tripwire_events::wave_4_close` + 7b.9 status (must be `done` before 7b.10 opens; if not, HALT).
4. **PRD §FR98** — `_bmad-output/planning-artifacts/prd-slab-7b-specialist-activation-eleven.md` §FR98. Dan greenfield contract: option-a sanctum-aligned SKILL.md + 6-file BMB sidecar + scaffold-v0.2 + narrow-lane creative-director aux contributions threaded across G1/G1A/G2.
5. **Sandbox-AC inventory `dan-api-tbd-pending`** — `docs/dev-guide/migration-ac-sandbox-inventory.json` §`dan-api-tbd-pending`. **T1 BLOCKING resolution: LLM-only OR third-party-API; default LLM-only; third-party-API requires party-mode + version bump per B1/C1.**
6. **Class-A precedent (Texas/Quinn-R/Vera)** — Class-A 6-file BMB pattern is the closest sanctum-shape analog; consult `_bmad-output/implementation-artifacts/migration-7b-1-texas-hardening.md` + `migration-7b-2-quinn-r-hardening.md` for sanctum file content patterns.
7. **`bmad-create-specialist` skill** — `.claude/skills/bmad-create-specialist/` (or canonical equivalent). This is the generator invocation path for AC-B.
8. **Slab 2a.2 Class-A precedent (sanctum cold-read pattern)** — `_bmad-output/implementation-artifacts/migration-2a-2-irene-pass-2-scaffold-migration.md`.
9. **Specialist migration template (R1-R14)** — `docs/dev-guide/specialist-migration-template.md`.
10. **CLAUDE.md** — §LangChain/LangGraph migration governance + NFR-CG13/19/20 + bmad-memory-gitignore-force-add-policy + B1/C1 sandbox-AC promotion gating.

## T1 hard checkpoints (HALT-AND-SURFACE if violated)

- Round-(e) governance pin verified (`d['version'] == '2026-04-29-slab7b-twelve-stories'`; `d['stories']['7b-10']['expected_gate_mode'] == 'single-gate'`; `d['stories']['7b-10']['k_contract']['tripwire_threshold_kloc'] == 4.0`).
- Wave 1 + 2a + 2b + 3 + 4 all `done` (8 stories; 7b.1 through 7b.9).
- Class-A/B/C+/C templates active in validator from 7b.1-7b.9 closes (verified via `validate_parity_test_class_conformance.py tests/parity/` PASS).
- Dan baseline at `app/specialists/dan/` does NOT yet exist (greenfield posture confirmed).
- `_bmad/memory/bmad-agent-dan/` does NOT yet exist (greenfield).
- `skills/bmad-agent-dan/` does NOT yet exist (greenfield).
- `_bmad/memory/dan-sidecar/` exists (legacy pre-Slab-7b artifact; consult for content; preserved out-of-band post-trial-2; cleanup follow-on filed at T3.2).
- `bmad-create-specialist` skill exists and is invocable.
- Sandbox-AC validator pre-flight PASS.
- **`dan-api-tbd-pending` resolution recorded** at T1.6 (Dev Agent Record). HALT if third-party-API surfaces — operator must convene party-mode.

## Files in scope

**New (≥12 files; greenfield posture):**
- `_bmad/memory/bmad-agent-dan/INDEX.md` + `PERSONA.md` + `CREED.md` + `BOND.md` + `MEMORY.md` + `CAPABILITIES.md` — 6-file BMB sanctum (canonical Class-A pattern; novel content per BMB checklist; consult `dan-sidecar/` for narrative content)
- `skills/bmad-agent-dan/SKILL.md` — NEW persona-skill (Class-D1 single-SKILL.md per FR98; minimal FR101 R1 frontmatter `name: bmad-agent-dan` + persona-focused description; body = activation hot-load batch referencing `_bmad/memory/bmad-agent-dan/` BMB sanctum). NOTE: Class-D1 is single-SKILL.md (no API-mastery sibling) since LLM-only is the default.
- `app/specialists/dan/__init__.py` + `_act.py` + `graph.py` + `state.py` + `model_config.yaml` + `config.yaml` — scaffold-v0.2 instantiation via `bmad-create-specialist`
- `tests/parity/test_dan_activation_contract.py` — flat layout; **NEW Class-D1 template** (`class_template_id = "D1"`; `specialist_name = "dan"`)
- `tests/specialists/dan/test_dan_aux_contributions_g1_g2.py` — verifies G1/G1A/G2 aux-contribution shape per FR98
- `tests/specialists/dan/test_dan_summary_landing.py` — 7a.5 facade integration
- `tests/composition/test_dan_to_compositor_chain.py` — fixture-replay until 7b.11 lands
- `_bmad-output/implementation-artifacts/7b-10-codex-self-review-2026-04-XX.md` — T10 G6 self-review

**Modified:**
- `scripts/utilities/validate_parity_test_class_conformance.py` — **NEW Class-D1 template assertions** (LOCKSTEP foundational deliverable; first D1 close)
- `docs/dev-guide/migration-ac-sandbox-inventory.json` — RETIRE `dan-api-tbd-pending` entry at T2.5 (LLM-only path) OR REPLACE via party-mode + version bump (third-party-API path)
- `_bmad-output/planning-artifacts/deferred-inventory.md` — file `dan-sidecar-cleanup-post-trial-2-validation` named-but-not-filed follow-on at T3.2

**Do NOT modify:**
- `app/marcus/orchestrator/dispatch_adapter.py` lines 70-95 (substrate-frozen).
- 7b.1-7b.9 substrate (consume only; class A/B/C+/C templates inherited).
- Class-A/B/C+/C template assertions in validator (extend ONLY for D1; do not modify A/B/C+/C).
- `_bmad/memory/dan-sidecar/` (legacy; consult for content; preserved out-of-band; not deleted by this story).

## Critical implementation notes

- **`dan-api-tbd-pending` T1 resolution (BLOCKING):** record decision in Dev Agent Record T1 block. Default LLM-only (no operator gate; retire entry at T2.5 in same commit). If operator surfaces design-mandated third-party-API constraint, HALT — operator convenes party-mode per B1/C1 binding-hard.
- **bmad-create-specialist invocation (AC-B):** generator parameters: `specialist_name=dan`, `class_template_id=D1`, `scaffold_version=v0.2`, `sanctum_path=_bmad/memory/bmad-agent-dan/`, `skill_path=skills/bmad-agent-dan/SKILL.md`, `app_path=app/specialists/dan/`. Generator denylist (Slab 2a.1) does NOT block; Dan is first Slab 7b D1 greenfield; permitted per FR98.
- **9-node scaffold-v0.2 conformance:** `validate_scaffold("dan", build_dan_graph()).is_conforming is True`. Generator emits canonical `SCAFFOLD_NODE_IDS`.
- **Single-SKILL.md pattern (NOT two-SKILL.md):** Class-D1 is greenfield with NO pre-existing API-mastery skill (Dan never had one); single SKILL.md at `skills/bmad-agent-dan/SKILL.md` is canonical. (Two-SKILL.md is Class-C-only per Round-(f) ratification.)
- **`_act` body shape (FR98 primary):** narrow-lane creative-director aux contributions threaded across gates:
  - **G1 contribution:** creative-director critique on draft outline (prose; ≤300 words/segment).
  - **G1A contribution:** narrative-arc check on cluster boundaries (prose; ≤200 words).
  - **G2 contribution:** tone-and-voice consistency review on Pass-2 narration (prose; ≤300 words/segment).
- **AC-B 150-LOC ceiling on `_act` body.** Dan's body invokes the shared LLM facade (no third-party HTTP); cache-hit-rate harness applies (FR106 — Dan is the 10th LLM specialist).
- **Cache-hit-rate (FR106):** Dan participates in the 10-LLM-specialist harness aggregation; `median[2:] >= 85%` post-warm-up. Add Dan to `tests/parity/test_cache_hit_rate_harness.py` parametrize list (or wherever harness aggregator lives).
- **Class-D1 template extension (LOCKSTEP):** add D1 assertions to `validate_parity_test_class_conformance.py`. Pattern: `class_template_id = "D1"` requires (i) sanctum at `_bmad/memory/bmad-agent-dan/` with 6-file BMB; (ii) skill at `skills/bmad-agent-dan/SKILL.md` (single, NOT two-SKILL); (iii) scaffold-v0.2 conformance via `validate_scaffold`; (iv) aux-contribution shape per FR98 (G1/G1A/G2 prose contributions).
- **Live-API discipline (NFR-CG13 strict):** Dan is LLM-only via shared facade; no live HTTP. CI tests use shared LLM cache fixtures (no VCR cassettes needed unless surface area expands).
- **Credential register (NFR-CG19):** N/A for LLM-only (LLM credentials managed at facade level). Skip Wondercraft/Gamma-style row.
- **Rate-limit budget (NFR-CG20):** declare in `app/specialists/dan/config.yaml` (LLM token-budget per minute; coordinate with shared facade rate-limiter).
- **K-contract tripwire 4.0K binding-hard:** if cumulative LOC count >4.0K (per `wc -l` net of imports/comments), HALT and surface to operator + party-mode for scope-review per Round-(e) E6/Murat. Plausibly signals API-integration leak (third-party-API drift).
- **PyYAML, NOT ruamel.** No new third-party deps. Sanctum gitignored — Claude T11 commit uses `git add --force` for `_bmad/memory/bmad-agent-dan/`.

## Verification battery (T9)

```bash
.venv/Scripts/python.exe -m pytest tests/parity/test_dan_activation_contract.py tests/specialists/dan tests/composition/test_dan_to_compositor_chain.py tests/parity/test_skill_md_sanctum_alignment.py tests/parity/test_cache_hit_rate_harness.py -q --tb=short
.venv/Scripts/python.exe -m pytest tests/unit/manifest tests/integration/marcus tests/composition tests/parity tests/structural tests/unit/marcus tests/specialists tests/cli tests/unit/models -q --tb=line --ignore=tests/integration/marcus/test_directive_confirm_or_edit_prompt.py
.venv/Scripts/python.exe scripts/utilities/check_pipeline_manifest_lockstep.py
.venv/Scripts/python.exe scripts/utilities/detect_live_api_in_tests.py
.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7b-10-dan-greenfield.md
.venv/Scripts/python.exe scripts/utilities/validate_parity_test_class_conformance.py tests/parity/    # MUST pass with NEW D1 template active
.venv/Scripts/python.exe -m ruff check app/specialists/dan tests/parity/test_dan_activation_contract.py tests/specialists/dan tests/composition/test_dan_to_compositor_chain.py
.venv/Scripts/lint-imports.exe
```

Expected: zero new failures vs post-7b.9 baseline. **Class-D1 template now active in validator** (5 classes total: A/B/C+/C/D1). **`dan-api-tbd-pending` entry RETIRED** from sandbox-AC inventory (LLM-only path).

## T10 + T11

- **T10 (Codex):** G6 self-review at `_bmad-output/implementation-artifacts/7b-10-codex-self-review-2026-04-XX.md`. Flip status `in-progress → review`.
- **T11 (Claude):** bmad-code-review at `7b-10-code-review-2026-04-XX.md`; remediation cycle 1 if PASS-WITH-PATCH; AC-10-B is CONDITIONAL — N/A if LLM-only resolution at T1; mandatory operator-gated canary if third-party-API; **append `wave_5a_close` ledger entry** to `sprint-status.yaml::tripwire_events`; if k_contract tripwire fired (>4.0K), record in ledger + party-mode escalation; sprint-status flip done; commit + push (force-add gitignored sanctum); next-session-start-here.md pivot to 7b.11 Wave-5b Compositor open.

## Boundary

**HALT-AND-SURFACE on:**
- (a) 7b.9 Wanda not `done` in sprint-status (Wave-4 close incomplete) — strict prereq
- (b) `dan-api-tbd-pending` resolution surfaces third-party-API constraint at T1.6 — operator must convene party-mode per B1/C1 binding-hard; do NOT proceed unilaterally
- (c) Round-(e) governance pin mismatch
- (d) AC-B 150-LOC ceiling exceeded
- (e) substrate-frozen-paths violation
- (f) sandbox-AC violation
- (g) live-API import detected by AST scan in CI test files (LLM-only path; no third-party HTTP allowed)
- (h) sanctum 6-file BMB pattern drift from canonical (must match `INDEX/PERSONA/CREED/BOND/MEMORY/CAPABILITIES` exactly; novel content per BMB checklist)
- (i) Class-D1 template extension breaks A/B/C+/C inheritance (validator must PASS for ALL existing classes + NEW D1)
- (j) `bmad-create-specialist` generator denylist blocks Dan — flag immediately (should NOT block; if it does, generator bug)
- (k) k_contract tripwire 4.0K exceeded — HALT, record in ledger, party-mode escalation per Round-(e) E6/Murat (likely scope creep / API integration leak)
- (l) Cache-hit-rate harness post-warm-up rate <85% for Dan slot — investigate prompt-cache wiring before continuing

**Do NOT:**
- Touch substrate-frozen lines
- Modify `_bmad/memory/dan-sidecar/` (legacy; preserved out-of-band; cleanup follow-on filed at T3.2)
- Modify 7b.1-7b.9 substrate (parity base, chain base, validator A/B/C+/C templates, prior story scaffolds)
- Promote `dan-api-tbd-pending` inventory entry from forbidden to `dev_agent_available` without party-mode + version bump (B1/C1 binding-hard)
- Introduce ruamel.yaml or new third-party deps
- Author `tests/parity/per_specialist/` subdir (Errata 4 verdict-flat)
- Author two-SKILL.md pattern (Class-D1 is single-SKILL.md per FR98; two-SKILL.md is Class-C-only per Round-(f))
- Add Wondercraft/Gamma/Kling/ElevenLabs API client invocations (Dan is LLM-only via shared facade)
- Skip the cache-hit-rate harness participation (Dan is the 10th LLM specialist per FR106)
- Skip the `dan-api-tbd-pending` entry retirement at T2.5 (must land in same commit as scaffold)
```
