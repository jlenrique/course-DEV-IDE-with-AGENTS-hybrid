# Codex dev-story prompt — Story 7b.8 Enrique Port-Shape (Slab 7b Wave-3 parallel)

**Cycle:** Claude spec → Codex dev+tests → Claude bmad-code-review + commit + flip done.
**Wave:** 3 parallel — PARALLEL with 7b.6 Gary (done) + 7b.7 Kira (in-progress). Opens once 7b.6 reaches `done` (already satisfied 2026-04-29).
**Gate:** **SINGLE-GATE** (resolved 2026-04-29 per Round-(e) E3 conditional_gate_override default; 7b.6 first-port tripwire NOT fired; verified `wave_3_first_port_tripwire::fired_verdict: false`).
**Class:** C API-bound (ElevenLabs API; third-party).

**Class-C two-SKILL.md convention RATIFIED 2026-04-29 (party-mode 4/4 unanimous on option (a); binding for 7b.8):**
- **CREATE NEW persona-skill at `skills/bmad-agent-enrique/SKILL.md`** with minimal FR101 R1-compliant frontmatter (`name: bmad-agent-enrique` + persona-focused description); body = activation hot-load batch referencing `_bmad/memory/bmad-agent-enrique/` BMB sanctum + line documenting "Use `skills/bmad-agent-elevenlabs/` only as ElevenLabs API reference material; runtime execution via `app/specialists/enrique/`."
- **PRESERVE** `skills/bmad-agent-elevenlabs/SKILL.md` UNTOUCHED — Slab 2b.x era ElevenLabs API-mastery skill; consume lazily as API reference; NOT modified by this story.
- Mirrors 7b.6 Gary pattern (persona at `bmad-agent-gary/`; API-mastery at `bmad-agent-gamma/`).

**Note: `enrique` ↔ `elevenlabs` SPECIALIST_ALIASES** per `app/manifest/compiler.py:43-46` carry-forward; specialist_id mapping enforced in summary writer + dispatch registry + tests.

**STATUS:** Spec READY-FOR-DEV at `_bmad-output/implementation-artifacts/migration-7b-8-enrique-port-shape.md` (Claude-authored 2026-04-29; sandbox-AC validator PASS; 14 ACs A-N + 11 task blocks; Drift #2 amended to two-SKILL.md ratified-binding).

---

```
Run bmad-dev-story on Story 7b.8 (Slab 7b Wave-3 parallel; Class-C API-bound; SINGLE-GATE per Round-(e) E3 default; ElevenLabs API live invocation + voice-preview/voice-selection HIL contract + manifest-driven narration on locked package + assembly-bundle build + per-segment progress).

## Required reading (read in order)

1. **Story spec:** `_bmad-output/implementation-artifacts/migration-7b-8-enrique-port-shape.md` (status: ready-for-dev; 14 ACs A-N; 11 tasks; you own T1-T10; Claude owns T11 close).
2. **Round-(e) governance JSON** — `docs/dev-guide/migration-story-governance.json` §`stories.7b-8.conditional_gate_override` (trigger_story=7b-6; binding=hard; **NOT fired** since 7b.6 closed under 2.7K → single-gate default applies).
3. **Wave-3 first-port close-verdict** — read `sprint-status.yaml::tripwire_events::wave_3_first_port_tripwire` (verified `fired_verdict: false` 2026-04-29 by 7b.6 T13 close; 7b.8 OPENS SINGLE-GATE).
4. **7b.6 Gary precedent (Class-C TEMPLATE; immediate predecessor)** — `_bmad-output/implementation-artifacts/migration-7b-6-gary-port-shape.md` + `_bmad-output/implementation-artifacts/7b-6-code-review-2026-04-29.md`. Inherit Class-C template (validator), 6-file BMB sanctum at `bmad-agent-{specialist}/`, VCR cassettes, NFR-CG13/19/20, operator-gated AC-N-B canary, **two-SKILL.md convention** (persona at specialist-name + API-mastery at API-name).
5. **PRD §FR97** — `_bmad-output/planning-artifacts/prd-slab-7b-specialist-activation-eleven.md` §FR97. ElevenLabs API + voice-preview/voice-selection HIL contract + manifest-driven narration + assembly-bundle build + per-segment progress.
6. **Sandbox-AC inventory entry `elevenlabs` (FR107; Wave 0 LANDED)** — `docs/dev-guide/migration-ac-sandbox-inventory.json` §`elevenlabs`.
7. **7b.7 Kira parallel sibling (mirror Class-C two-SKILL.md pattern)** — `_bmad-output/implementation-artifacts/migration-7b-7-kira-port-shape.md`. Same Round-(e) E3 single-gate default + two-SKILL.md ratified-binding.
8. **Slab 2b.1 TEMPLATE precedent** — `_bmad-output/implementation-artifacts/migration-2b-1-gary-scaffold-migration.md`.
9. **`scripts/api_clients/elevenlabs_client.py`** — ElevenLabs API client (already shipped; Slab 2b.x era).
10. **CLAUDE.md** — §LangChain/LangGraph migration governance + NFR-CG13/19/20 + `enrique` ↔ `elevenlabs` SPECIALIST_ALIASES handling + bmad-memory-gitignore-force-add-policy.

## T1 hard checkpoints (HALT-AND-SURFACE if violated)

- Round-(e) E3 trigger-story binding verified (`d['stories']['7b-8']['conditional_gate_override']['trigger_story'] == '7b-6'`; `binding: 'hard'`).
- 7b.6 (Wave-3 first-port) status `done` in sprint-status.yaml. ✅ verified 2026-04-29.
- `wave_3_first_port_tripwire` ledger entry exists with `fired_verdict: false` → 7b.8 OPENS SINGLE-GATE.
- Wave-1 + Wave-2a + Wave-2b + Wave-3-first-port all closed.
- Class-C template active in validator from 7b.6 close (verified via `validate_parity_test_class_conformance.py tests/parity/` PASS — should show 7+ activation contracts post-7b.6 + post-Codex's 7b.7 in-progress).
- Enrique baseline at `app/specialists/enrique/`: `__init__.py expertise/ elevenlabs_dispatch.py graph.py model_config.yaml state.py` (Slab 2b era; ElevenLabs dispatch present).
- `_bmad/memory/bmad-agent-enrique/` does NOT yet exist (sanctum greenfield; this story creates 6-file BMB).
- `skills/bmad-agent-elevenlabs/` exists (verified) — Slab 2b.x era API-mastery skill; PRESERVED untouched.
- `skills/bmad-agent-enrique/` does NOT yet exist (this story creates per two-SKILL.md ratification).
- `scripts/api_clients/elevenlabs_client.py` exists.
- FR107 sandbox-AC `elevenlabs` entry present.
- Sandbox-AC validator pre-flight PASS.

## Files in scope

**New (≥10 files):**
- `_bmad/memory/bmad-agent-enrique/INDEX.md` + `PERSONA.md` + `CREED.md` + `BOND.md` + `MEMORY.md` + `CAPABILITIES.md` — 6-file BMB sanctum (Class-C; specialist-name path)
- `skills/bmad-agent-enrique/SKILL.md` — NEW persona-skill (Class-C two-SKILL.md convention; minimal FR101 R1 frontmatter `name: bmad-agent-enrique` + persona-focused description; body = activation hot-load batch referencing `_bmad/memory/bmad-agent-enrique/` + line documenting `skills/bmad-agent-elevenlabs/` is API-mastery reference material consumed lazily)
- `tests/parity/test_enrique_activation_contract.py` — flat layout; Class-C template (`class_template_id = "C"`; `specialist_name = "enrique"`)
- `tests/specialists/enrique/test_enrique_voice_selection_hil.py` — VCR cassette; voice-preview-options.json + voice-selection-review.md + voice-selection.json artifact emission
- `tests/specialists/enrique/test_enrique_assembly_bundle_build.py` — VCR cassette; `assembly-bundle/audio/` + `captions/` populated + per-segment stderr progress
- `tests/specialists/enrique/test_enrique_no_live_api_in_ci.py` — AST-scan
- `tests/specialists/enrique/test_enrique_summary_landing.py` — 7a.5 facade integration; verifies enrique↔elevenlabs aliasing
- `tests/composition/test_enrique_to_compositor_chain.py` — fixture-replay until 7b.11 lands
- `tests/fixtures/specialist-replay/enrique/*.yaml` — VCR cassettes
- `_bmad-output/implementation-artifacts/7b-8-codex-self-review-2026-04-XX.md` — T10 G6 self-review

**Modified:**
- `app/specialists/enrique/_act.py` — refine bounded body; ≤150 LOC AC-B ceiling; invoke `elevenlabs_client.py`
- `app/specialists/enrique/graph.py` — additive delegation pattern (mirror prior closed Class-A/B/C+/C precedents: `_act = _enrique_act_impl.act`)
- `app/specialists/enrique/config.yaml` — NEW or EXTENDED (rate-limit budget per NFR-CG20)
- `state/config/credential-rotation-register.yaml` — ADD ElevenLabs API row
- (NO `validate_parity_test_class_conformance.py` extension — Class-C template inherited from 7b.6 unchanged)

**Do NOT modify:**
- `app/marcus/orchestrator/dispatch_adapter.py` lines 70-95 (substrate-frozen).
- 7b.1-7b.6 substrate (consume only).
- `skills/bmad-agent-elevenlabs/SKILL.md` (PRESERVED untouched per two-SKILL.md ratification; Slab 2b.x API-mastery content stays intact).
- Legacy `elevenlabs_dispatch.py` semantics (consume as helper).
- `scripts/api_clients/elevenlabs_client.py` (the API client; consume only).
- Class-C template assertions in validator (inherited from 7b.6 unchanged).

## Critical implementation notes

- **9-node scaffold per Slab 2b.1 TEMPLATE:** Enrique baseline already has scaffold from Slab 2b era; refine `_act` body, KEEP scaffold.
- **Two-SKILL.md ratified-binding:** CREATE `skills/bmad-agent-enrique/SKILL.md` (persona); PRESERVE `skills/bmad-agent-elevenlabs/SKILL.md` (API-mastery). Per 7b.6 Gary precedent.
- **Single-gate at story-open (Round-(e) E3 default):** 7b.6 first-port tripwire NOT fired; record resolved gate-mode (single) in T1.6 Drift Resolution + Dev Agent Record.
- **Class-C template inherited from 7b.6 (NO new template extension):** validator already supports Class-C; Enrique parity test passes with `class_template_id = "C"`. NO lockstep validator extension this story.
- **Voice-selection HIL contract (FR97 primary):** emit `voice-preview-options.json` (N candidate voices per run-constants) → operator reviews via `voice-selection-review.md` (markdown one-line-per-voice with recommended marker) → operator's selection lands in `voice-selection.json`. All under `[BUNDLE_PATH]/voice-selection/`.
- **Manifest-driven narration on locked package:** post-voice-selection; Enrique reads locked Pass-2 narration script + storyboard manifest; emits per-segment audio + captions.
- **Assembly-bundle build:** narration audio at `[BUNDLE_PATH]/assembly-bundle/audio/<segment_id>.{mp3|wav}`; captions at `[BUNDLE_PATH]/assembly-bundle/captions/<segment_id>.vtt`; per-segment progress emitted to stderr (`Enrique segment <id> [N/total] OK | duration=<s>s | cost=<usd>`).
- **AC-B 150-LOC ceiling on `_act` body.**
- **Live-API discipline (NFR-CG13 strict):** All Enrique tests use VCR cassettes under `tests/fixtures/specialist-replay/enrique/`. Live canary belongs ONLY in operator-gated AC-8-B Completion-Notes block.
- **Cache-hit-rate N/A for Class-C:** Enrique is REST-API tool-dispatch (no LLM at Enrique layer; same as Gary/Kira).
- **Credential register (NFR-CG19):** ADD ElevenLabs row at `state/config/credential-rotation-register.yaml`.
- **Rate-limit budget (NFR-CG20):** declare in `app/specialists/enrique/config.yaml`.
- **`enrique` ↔ `elevenlabs` aliasing:** per `app/manifest/compiler.py::SPECIALIST_ALIASES`. AC-L explicitly verifies aliasing in summary-writer integration.
- **PyYAML, NOT ruamel.** No new third-party deps. Sanctum gitignored — Claude T11 commit uses `git add --force` for `_bmad/memory/bmad-agent-enrique/`.

## Verification battery (T9)

```bash
.venv/Scripts/python.exe -m pytest tests/parity/test_enrique_activation_contract.py tests/specialists/enrique tests/composition/test_enrique_to_compositor_chain.py tests/parity/test_skill_md_sanctum_alignment.py -q --tb=short
.venv/Scripts/python.exe -m pytest tests/unit/manifest tests/integration/marcus tests/composition tests/parity tests/structural tests/unit/marcus tests/specialists tests/cli tests/unit/models -q --tb=line --ignore=tests/integration/marcus/test_directive_confirm_or_edit_prompt.py
.venv/Scripts/python.exe scripts/utilities/check_pipeline_manifest_lockstep.py
.venv/Scripts/python.exe scripts/utilities/detect_live_api_in_tests.py
.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7b-8-enrique-port-shape.md
.venv/Scripts/python.exe scripts/utilities/validate_parity_test_class_conformance.py tests/parity/
.venv/Scripts/python.exe -m ruff check app/specialists/enrique tests/parity/test_enrique_activation_contract.py tests/specialists/enrique tests/composition/test_enrique_to_compositor_chain.py
.venv/Scripts/lint-imports.exe
```

Expected: zero new failures vs post-7b.6 baseline (pre-existing Wanda + Desmond live-LLM smoke flakes remain; both filed and out-of-scope).

## T10 + T11

- **T10 (Codex):** G6 self-review at `_bmad-output/implementation-artifacts/7b-8-codex-self-review-2026-04-XX.md`. Flip status `in-progress → review`.
- **T11 (Claude):** bmad-code-review at `7b-8-code-review-2026-04-XX.md`; remediation cycle 1 if PASS-WITH-PATCH; operator-gated AC-8-B if window opens; **append wave_3_parallel_close ledger entry with 7b.8 contribution** (separate from wave_3_first_port_tripwire from 7b.6); sprint-status flip done; commit + push (force-add gitignored sanctum); next-session-start-here.md pivot to 7b.9 Wave-4 open.

## Boundary

**HALT-AND-SURFACE on:**
- (a) 7b.6 not at `done` (need close-verdict in ledger before this story can resolve gate-mode) — already satisfied 2026-04-29
- (b) `wave_3_first_port_tripwire` ledger entry absent or `fired_verdict` not `false` (single-gate must be the resolved mode)
- (c) Round-(e) E3 binding-hard pin mismatch
- (d) AC-B 150-LOC ceiling exceeded
- (e) substrate-frozen-paths violation
- (f) sandbox-AC violation
- (g) live-API import detected by AST scan in CI test files
- (h) sanctum 6-file BMB pattern drift from Class-A/C precedent (must match 6-file pattern at `_bmad/memory/bmad-agent-enrique/`)
- (i) Class-C template inheritance breaks (validator must PASS without modification)
- (j) credential register + rate-limit budget entries missing (NFR-CG19/CG20)
- (k) two-SKILL.md ratified-binding violated (must CREATE `skills/bmad-agent-enrique/SKILL.md` AND must NOT modify `skills/bmad-agent-elevenlabs/SKILL.md`)
- (l) `enrique` ↔ `elevenlabs` SPECIALIST_ALIASES not respected in summary-writer or dispatch registry

**Do NOT:**
- Touch substrate-frozen lines
- Modify legacy `elevenlabs_dispatch.py` semantics (consume as helper)
- Modify `scripts/api_clients/elevenlabs_client.py` (consume only)
- Modify 7b.1-7b.7 substrate (parity base, chain base, validator A/B/C+/C templates, prior story scaffolds)
- Extend Class-C template assertions in validator (inherited from 7b.6 without modification)
- Modify `skills/bmad-agent-elevenlabs/SKILL.md` (PRESERVED per two-SKILL.md ratification)
- Introduce ruamel.yaml or new third-party deps
- Author `tests/parity/per_specialist/` subdir (Errata 4 verdict-flat)
- Run live ElevenLabs API in CI (NFR-CG13 strict)
- Skip the voice-selection HIL contract (3 artifacts: voice-preview-options.json + voice-selection-review.md + voice-selection.json)
- Skip per-segment stderr progress emission
```
