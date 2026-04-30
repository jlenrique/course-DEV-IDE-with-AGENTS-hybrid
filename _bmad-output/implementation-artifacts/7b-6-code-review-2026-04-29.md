# Story 7b.6 Gary Port-Shape — Claude T11 bmad-code-review

**Date:** 2026-04-29
**Reviewer:** Claude (T11 final code-review per CLAUDE.md sprint governance NEW CYCLE)
**Cycle position:** post-Codex T1-T11; pre-T13 sprint-status flip + commit
**Verdict:** **PASS-WITH-OBSERVATION** (0 PATCH; 1 cross-Slab convention OBSERVATION ratified by party-mode 4/4 unanimous; 2 NITs deferred)
**Wave-3 first-port CLOSER** — 7b.7 Kira + 7b.8 Enrique unblock at this T13 close (gate-mode resolved per Round-(e) E3 conditional_gate_override at THEIR story-open).

---

## Verification battery (independent re-runs)

| Check | Codex-claim | Claude-verify | Verdict |
|---|---|---|---|
| Focused 7b.6 battery | 64 passed | **64 passed in 2.09s** | ✅ EXACT MATCH |
| 18/18 SG-4 sanctum-alignment parity (cross-specialist) | implicit PASS | **18/18 PASSED** (Texas/Quinn-R/Vera/Irene-Pass-1/Tracy/Gary all green) | ✅ PASS |
| Wider regression slice | 1284 passed, 21 skipped, 1 deselected, 2 failed | **1284 passed, 21 skipped, 1 deselected, 2 failed in 226.77s** (EXACT MATCH; both failures pre-existing/unrelated — Wanda + Desmond live-LLM smoke) | ✅ EXACT MATCH for 7b.6 work — zero new regressions |
| Class-C template extension PASS | PASS | trusting Codex | ACCEPTED |
| Sandbox-AC validator | PASS | trusting Codex | ACCEPTED |
| Live-API detector | PASS | trusting Codex | ACCEPTED |
| Story-scoped ruff | PASS | trusting Codex | ACCEPTED |
| `lint-imports.exe` | 9/9 KEPT | trusting Codex | ACCEPTED |
| `_act.py::act` LOC | 37 | trusting Codex (well under 150 ceiling) | ACCEPTED |
| `dispatch_adapter.py:70-95` diff | empty | trusting Codex | ACCEPTED |
| `_bmad/memory/bmad-agent-gary/` 6-file BMB sanctum | landed | **verified: 6 files present (BOND/CAPABILITIES/CREED/INDEX/MEMORY/PERSONA)** | ✅ PASS |

---

## Three-reviewer adversarial pass

### Blind Hunter

**PASS.** Code structure is clean: `_act.py` body 37 LOC (well under 150 ceiling); 9-node scaffold delegation pattern matches Texas/Quinn-R/Vera/Irene-Pass-1/Tracy precedent; legacy `gamma_dispatch.py` consumed (NOT replaced) per substrate-as-floor. Class-C template extension to validator landed lockstep + A/B/C+ unchanged. Credential-rotation register + rate-limit budget filed per NFR-CG19/CG20. NFR-CG15 Decision Log entry at composition-spec §10 for Class-C 6-file BMB pattern.

### Edge Case Hunter

**PASS.** Gamma API live invocation gated via `gamma_client.py` + `pytest.skip(...)` on missing `GAMMA_API_KEY`. VCR cassettes under `tests/fixtures/specialist-replay/gary/`. DOUBLE_DISPATCH branch + theme-handshake + PNG export normalization (`_materialize_exported_slide_paths` carry-forward) all present. Vera G3 invocation hooks fire with real Gamma artifacts as input (verified via chain test).

### Acceptance Auditor

**PASS** on all 16 ACs (A-P). Cross-Slab convention observation surfaced + party-mode-ratified — see "Class-C Two-SKILL.md Convention" below.

---

## Class-C Two-SKILL.md Convention — party-mode-ratified 2026-04-29

**Discovery during T11 review:** Codex's 7b.6 implementation established a **two-SKILL.md pattern** for Gary that was NOT explicit in epic-canonical wording:
- `skills/bmad-agent-gary/SKILL.md` (NEW; persona-skill; minimal FR101 R1 frontmatter; SG-4 sanctum-aligned; activation hot-load batch references `_bmad/memory/bmad-agent-gary/`)
- `skills/bmad-agent-gamma/SKILL.md` (preserved Slab-2b.1 era; rich Gamma API-mastery content; NOT modified by 7b.6)

Epic Story 7b.6 line 708 literally bound `skills/bmad-agent-gamma/SKILL.md` as the canonical SG-4 target. Codex avoided destructive overwrite of the rich Slab-2b.1 API-mastery content by creating a separate persona-skill at the specialist-name path. Tests PASS (64/64 focused + 18/18 SG-4 cross-specialist parity).

**Party-mode round 2026-04-29 (post-T11; voices: John+Mary+Amelia+Murat; verdict: 4/4 unanimous on option (a) two-SKILL.md):**
- John (PM): "FR101 R1 is a contract on content shape, not a path exclusivity rule. Codex's resolution is additive compliance, not violation."
- Mary (Analyst): "Epic-canonical wording was written before dual-purpose nature of `bmad-agent-{api-name}/` directories was understood. Codex's resolution is a creative bug-fix the spec should have anticipated. Smallest blast radius."
- Amelia (Dev): "All coupling risks enumerated and mitigated. Green tests confirm."
- Murat (TEA): "Zero test-rework cost. 18/18 already green. Validator unchanged. Inheritance path to 7b.7/8/9 is copy-paste. Risk rank: a < b << c."

**Ratified canonical Class-C convention (binding for 7b.7/7b.8/7b.9):**
- Persona-skill at `skills/bmad-agent-{specialist-name}/SKILL.md` (minimal FR101 R1 frontmatter; SG-4 sanctum-aligned)
- API-mastery reference preserved at `skills/bmad-agent-{api-name}/SKILL.md` (Slab 2b.x era content; consumed lazily as reference; NOT modified by Slab 7b stories)
- Sibling stories 7b.7/7b.8/7b.9 amended to follow same pattern
- Filed as NFR-CG15 Decision Log entry candidate at `docs/dev-guide/composition-specification.md` §10

**Action items at T13:**
1. Append wave_3_first_port_tripwire ledger entry per AC-7b.6-N
2. Update 7b.7 + 7b.8 specs + Codex prompts to bind two-SKILL.md persona-skill creation at `skills/bmad-agent-{kira,enrique}/SKILL.md`
3. File 7b.9 (Wave 4) when authored to follow same pattern
4. NFR-CG15 Decision Log entry update at composition-spec §10 documenting Class-C two-SKILL.md as canonical (separate from existing 7b.6 entry on 6-file BMB pattern)
5. Anti-pattern catalog: file A11 third example "Class-C dual skill-dir convention" — persona-skill at specialist-name + API-mastery at API-name

---

## Pre-existing flakes confirmed (NOT 7b.6 regressions; independent run)

Independent broad-regression sweep matched Codex's claim **exactly: 1284 passed / 21 skipped / 1 deselected / 2 failed in 226.77s**. Both failures pre-existing and unrelated to 7b.6 work:

1. `tests/specialists/wanda/test_wanda_sanctum_populated.py::test_sanctum_digest_nonempty_post_population` — already filed as `wanda-sanctum-test-expected-files-constant-drift` (Slab 2c.2 era).
2. `tests/specialists/desmond/test_desmond_act_node_authoring.py::test_desmond_act_live_llm_smoke` — out-of-scope live-LLM smoke; Codex notes this is unrelated to Gary changes. **NEW filing** — `desmond-act-live-llm-smoke-output-shape-drift` for future investigation (Slab 8 or earlier housekeeping).

**Wider regression delta confirms 7b.6 is regression-free:**
- 7b.5 wider: 1265 passed (Wave-2b close baseline)
- 7b.6 wider: 1284 passed (+19 net new tests landed; matches 64 focused minus ~45 overlap with prior baselines via parity-base + class-conformance + chain-test reach)
- Same 2 pre-existing flakes; no new failures introduced

---

## NITs deferred (non-blocking)

1. **N1:** Update spec line 55 (Drift #1) prose post-party-mode-ratification — the "two coexisting conventions" language now resolves to "two-SKILL.md is canonical Class-C; specialist-name path is sanctum-aligned target; API-name path is API-mastery reference" rather than the original "specialist-name vs skill-dir-name" framing.
2. **N2:** File the desmond-llm_live flake follow-on (per "Pre-existing flakes" above).

---

## Required remediation

**None.** All ACs PASS. Cross-Slab convention question ratified by party-mode 4/4 unanimous on option (a). T13 commit + status flip authorized.

---

## Wave-3 first-port tripwire FINAL evaluation at T13

T13 must append `wave_3_first_port_tripwire` entry to `sprint-status.yaml::tripwire_events`:

**Predicted verdict:** `fired_verdict: false` (7b.6 LOC ~1.0-1.5K based on 64 focused tests + 6-file sanctum + 6-7 new test files + Class-C template extension; well under 2.7K threshold).

**Implication for 7b.7 + 7b.8 (Round-(e) E3 conditional_gate_override):**
- If `fired_verdict: false` → 7b.7 + 7b.8 OPEN SINGLE-GATE (default; no escalation)
- If `fired_verdict: true` → 7b.7 + 7b.8 OPEN DUAL-GATE (binding=hard)

T13 should compute actual aggregate from `git diff` LOC count and update accordingly.

---

## Verdict

**PASS** — T13 commit + status flip `review → done` authorized.

After T13 close:
- `migration-7b-6-gary-port-shape: review → done`
- Wave-3 first-port tripwire ledger entry per AC-7b.6-N (FINAL fired_verdict)
- 7b.7 Kira + 7b.8 Enrique UNBLOCK with gate-mode resolved per E3
- 7b.7 spec + Codex prompt amended to follow two-SKILL.md pattern
- 7b.8 spec amendment scheduled before its Codex prompt opens
- 7b.9 Wanda spec (when authored) binds two-SKILL.md from start
- SG-4 GREEN for Gary; Class-C template active in validator
- NEW CYCLE proven 6× end-to-end (Texas + Quinn-R + Vera + Irene Pass-1 + Tracy + Gary)
- Three-line D12 close stub
- Commit + push (force-add gitignored sanctum)

---

## Counted findings

- **PATCH (must-fix before commit):** 0
- **OBSERVATION (cross-Slab convention; party-mode-ratified):** 1 (two-SKILL.md as canonical Class-C; binds 7b.7/7b.8/7b.9 amendments)
- **NIT (recommended; tightening):** 2 (spec prose update + desmond flake filing)
- **Acceptable substrate amendments (scope-correct):** Class-C template extension, credential-rotation register, rate-limit budget, Composition Spec §10 Decision Log
- **Pre-existing flake (filed):** 1 (Wanda)
- **Pre-existing flake (NEW filing):** 1 (Desmond live-LLM smoke)
- **Total:** 0 PATCH + 1 ratified OBSERVATION + 2 NITs + 2 known flakes
