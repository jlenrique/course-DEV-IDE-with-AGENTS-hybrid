# Migration Story 7b.7: Kira Port-Shape â€” Kling API Live Invocation + Motion Generation

**Status:** done
**Sprint key:** `migration-7b-7-kira-port-shape`
**Epic:** Slab 7b Specialist Body Activation â€” `epic-slab-7b-specialist-activation-eleven`. **Wave 3 parallel** (Class-C API-bound; PARALLEL with 7b.6 Gary + 7b.8 Enrique once 7b.6 opens; Claude-authored spec / Codex dev per NFR-CG17 + D21).
**Pts:** 4 | **Gate:** **single (DEFAULT) â†’ dual (CONDITIONAL via Round-(e) E3 binding-hard `conditional_gate_override` keyed to 7b.6 first-port tripwire)** | **K-target:** ~1.4Ã— (target ~33 tests / floor ~25; ~2.9K LOC).
**Author:** **Claude** spec / **Codex** dev. **Review:** **Claude** T11 `bmad-code-review`.
**Wave-3 precondition:** 7b.6 (Gary first-port) opens (parallel; not strict-after); BUT Round-(e) E3 binding-hard requires sprint runner to read 7b.6 close-verdict at this story's open AND apply gate-mode override if 7b.6 first-port tripwire fired (>2.7K LOC).

---

## Round-(e) Governance Inheritance

Round-(e) freeze landed 2026-04-29. Load-bearing for 7b.7:

- **E3 binding-hard `conditional_gate_override`:** trigger_story = 7b-6; trigger_condition = 7b-6 closes >2.7K LOC; override_gate_mode = dual-gate; binding=hard. **Sprint runner MUST read `tripwire_escalation_record_path` (sprint-status.yaml::tripwire_events::wave_3_first_port_tripwire) at 7b.7 story-open and apply override if fired.**

**T1 readiness verification command:**
```bash
.venv/Scripts/python.exe -c "import json; d = json.load(open('docs/dev-guide/migration-story-governance.json', encoding='utf-8')); entry = d['stories']['7b-7']['conditional_gate_override']; assert entry['trigger_story'] == '7b-6'; assert entry['override_gate_mode'] == 'dual-gate'; assert entry['binding'] == 'hard'; print('Round-(e) E3 conditional_gate_override verified PASS for 7b-7')"
```

Then read tripwire ledger at story-open:
```bash
.venv/Scripts/python.exe -c "
import yaml
d = yaml.safe_load(open('_bmad-output/implementation-artifacts/sprint-status.yaml', encoding='utf-8'))
events = [e for e in d.get('tripwire_events', []) if e.get('tripwire_id') == 'wave_3_first_port_tripwire']
if not events:
    print('7b-6 not yet closed; HALT 7b-7 dev open')
elif events[-1]['fired_verdict'] is True or events[-1]['fired_verdict'] == 'true':
    print('TRIPWIRE FIRED â†’ 7b-7 OPENS DUAL-GATE')
else:
    print('TRIPWIRE NOT FIRED â†’ 7b-7 OPENS SINGLE-GATE (default)')
"
```

---

## T1 Readiness Block

### Required-readings cascade (10-reading)

1. **Round-(e) governance JSON** â€” `docs/dev-guide/migration-story-governance.json` Â§`stories.7b-7` + Â§`stories.7b-6` + read tripwire-events ledger for 7b-6 close-verdict.
2. **Epic + story-level scope** â€” [`epics-slab-7b-specialist-activation-eleven.md`](../planning-artifacts/epics-slab-7b-specialist-activation-eleven.md) Â§Story 7b.7 (lines 734-783).
3. **PRD Â§FR95** â€” Kling API live invocation + motion generation per `motion_plan.yaml` + per-slide `.progress.json` + terminal `.json` receipts + reviewer inspection pack at `[BUNDLE_PATH]/recovery/inspection/` + fail-closed budget rules.
4. **Sandbox-AC inventory entry `kling` (FR107; Wave 0 LANDED)** â€” [`docs/dev-guide/migration-ac-sandbox-inventory.json`](../../docs/dev-guide/migration-ac-sandbox-inventory.json) Â§`kling`.
5. **7b.6 Gary Class-C precedent (Wave-3 first-port; immediate predecessor)** â€” [`migration-7b-6-gary-port-shape.md`](migration-7b-6-gary-port-shape.md). Inherit: Class-C template (validator), 6-file BMB sanctum at `bmad-agent-{specialist}/`, VCR cassettes, NFR-CG13/19/20, operator-gated AC-N-B, Wave-3 first-port tripwire pattern.
6. **Slab 2b.1 TEMPLATE precedent** â€” [`migration-2b-1-gary-scaffold-migration.md`](migration-2b-1-gary-scaffold-migration.md).
7. **Specialist migration template (R1-R14)** â€” [`docs/dev-guide/specialist-migration-template.md`](../../docs/dev-guide/specialist-migration-template.md).
8. **`scripts/api_clients/kling_client.py` + `scripts/api_clients/kling_public_client.py`** â€” Kling API client (already shipped; Slab 2b.x era).
9. **`tripwire_events::wave_3_first_port_tripwire` ledger** â€” at `sprint-status.yaml`; read 7b.6 close-verdict; apply gate-mode override per Round-(e) E3 if fired.
10. **CLAUDE.md** â€” Â§LangChain/LangGraph migration governance + NFR-CG13/19/20.

### Kira current-state probe + drift surfacing

```bash
ls app/specialists/kira/                              # __init__.py expertise/ graph.py kling_dispatch.py model_config.yaml state.py (Slab 2b era; Kling dispatch present)
ls _bmad/memory/bmad-agent-kira/ 2>/dev/null          # NOT YET PRESENT â€” sanctum greenfield (Slab 7b convention)
ls skills/bmad-agent-kling/                           # SKILL.md + references/ (skill-dir uses kling per A11 pattern)
ls skills/bmad-agent-kira/ 2>/dev/null                # may or may not exist; check at T1
ls scripts/api_clients/kling_client.py scripts/api_clients/kling_public_client.py  # both exist
```

**Three drifts surface at T1 (mirror 7b.6 Gary pattern):**

**âš ï¸ Drift #1 â€” Sanctum dir path: skill-dir-name (`bmad-agent-kling/`) vs Slab 7b epic (`bmad-agent-kira/`):** Same A11 pattern as Gary. **Resolution at T1 (binding):** path = `_bmad/memory/bmad-agent-kira/` per Slab 7b specialist-name convention. Filed as deferred-inventory follow-on `kira-sanctum-path-resolution` â€” CLOSED at this story T2.

**âš ï¸ Drift #2 â€” Class-C two-SKILL.md convention (party-mode-ratified 2026-04-29 binding):** Per Round-(f) party-mode 4/4 unanimous on option (a) ratified post-7b.6 close: Class-C specialists use TWO SKILL.md files â€” persona-skill at specialist-name path + API-mastery preserved at API-name path. **Resolution at T1 (binding):**
- **CREATE** `skills/bmad-agent-kira/SKILL.md` (NEW persona-skill; minimal FR101 R1 frontmatter `name: bmad-agent-kira` + persona-focused description; body = activation hot-load batch referencing `_bmad/memory/bmad-agent-kira/` BMB sanctum). Mirrors 7b.6 Gary pattern at `skills/bmad-agent-gary/SKILL.md`.
- **PRESERVE** `skills/bmad-agent-kling/SKILL.md` UNTOUCHED â€” Slab 2b.x era Kling API-mastery skill with rich content; consumed lazily as API reference (line in NEW kira/SKILL.md says "Use `skills/bmad-agent-kling/` only as Kling API reference material; runtime execution via `app/specialists/kira/`").
- Filed as deferred-inventory follow-on `class-c-two-skill-md-convention-ratified` â€” CLOSED at this story T2.

**âš ï¸ Drift #3 â€” Existing `kling_dispatch.py` legacy module at `app/specialists/kira/`:** Slab-2b era carry-forward. Wave-3 hardening consumes it (NOT replaces) per substrate-as-floor invariant.

### Wave 0 + 7b.1 substrate + Wave-1/2a/2b/3-first-port sweeps

```bash
# Standard Wave-0 + 7b.1 substrate sweeps (per Slab 7b T1 pattern)
ls docs/dev-guide/bmb-sanctum-alignment-checklist.md docs/dev-guide/sanctum-exception-categories.json docs/dev-guide/operator-control-parity-template.md docs/dev-guide/migration-ac-sandbox-inventory.json skills/bmad-agent-cora/SKILL.md
ls tests/parity/_sanctum_parity_base.py tests/composition/_chain_test_base.py scripts/utilities/validate_parity_test_class_conformance.py

# Wave 1+2a+2b closed; Wave-3 first-port (7b.6 Gary) AT LEAST IN-PROGRESS (parallel; not strict-after)
.venv/Scripts/python.exe -c "
import yaml
d = yaml.safe_load(open('_bmad-output/implementation-artifacts/sprint-status.yaml', encoding='utf-8'))
done = lambda k: d['development_status'][k].startswith('done')
in_review_or_done = lambda k: d['development_status'][k].startswith(('done', 'review'))
assert all(done(k) for k in ('migration-7b-1-texas-hardening','migration-7b-2-quinn-r-hardening','migration-7b-3-vera-hardening','migration-7b-4-irene-pass1-refresh','migration-7b-5-tracy-port-shape-sidecar'))
# 7b.6 must be at least review (final fired_verdict known) before 7b.7 opens
assert in_review_or_done('migration-7b-6-gary-port-shape'), '7b-6 must be in review or done before 7b-7 opens (need fired_verdict)'
print('Wave-3 first-port verdict available')
"

# FR107 sandbox-AC `kling` entry present
.venv/Scripts/python.exe -c "import json; d = json.load(open('docs/dev-guide/migration-ac-sandbox-inventory.json', encoding='utf-8')); assert 'kling' in d['notes']; print('kling entry present')"

# Class-C template active in validator (from 7b.6)
.venv/Scripts/python.exe scripts/utilities/validate_parity_test_class_conformance.py tests/parity/  # PASS expected
```

### Sandbox-AC validator pre-flight

```bash
.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py \
  _bmad-output/implementation-artifacts/migration-7b-7-kira-port-shape.md
```
Expect PASS. All Kling API verification wraps via shipped `httpx` + `kling_client.py` with `pytest.skip(...)`.

### Standing pre-flight items

1-3. Standard (severance posture; substrate-frozen; NFR-T9-T12).
4. **Conditional gate-mode at story-open:** sprint runner reads 7b.6 close-verdict; applies dual-gate override if fired per Round-(e) E3.

---

## Story

As a **migration dev agent**,
I want **Kira to execute a Class-C port-shape â€” Kling API live invocation via `kling_client.py` + motion generation per `motion_plan.yaml` directive + per-slide `.progress.json` (intermediate; live progress) + terminal `.json` receipts (final; success/failure) + reviewer inspection pack emission at `[BUNDLE_PATH]/recovery/inspection/` + fail-closed budget rules â€” AND I want Kira's sanctum greenfield at `_bmad/memory/bmad-agent-kira/` (6-file BMB pattern) per Class-C inheritance from 7b.6**,
So that **(a) Trial-2 reaches G2F with real Kira motion clips generated per the motion plan and the operator can review motion-vs-narration coherence in the per-slide review pack, (b) fail-closed budget rules prevent runaway live-API cost, (c) reviewer inspection pack provides operator-actionable forensics on motion generation outcomes, and (d) SG-4 sanctum-alignment is enforced via Class-C template inheritance from 7b.6**.

---

## Acceptance Criteria

All ACs are dev-agent-executable (sandbox-AC compliant). Live-API verification wraps via `httpx` + `kling_client.py` with `pytest.skip(...)`; live canary deferred to operator-gated AC-7-B Completion-Notes.

### AC-7b.7-A â€” T1 readiness + gate-mode resolution + drift resolution

**Given** the Round-(e) E3 binding-hard `conditional_gate_override` + Wave-3 first-port (7b.6) close-verdict known
**When** the dev agent runs T1 readiness
**Then** all 10 readings cascade complete; Round-(e) verification command exits 0; tripwire ledger read; gate-mode resolved (single OR dual per 7b.6 close-verdict)
**And** Drift #1 resolution recorded: sanctum path = `_bmad/memory/bmad-agent-kira/` (Slab 7b specialist-name)
**And** Drift #2 resolution recorded: SKILL.md canonical = `skills/bmad-agent-kling/SKILL.md` (per epic Story 7b.7 line 764; differs from Gary's Slab 7b-resolution which uses specialist-name skill-dir)
**And** Drift #3 acknowledged: legacy `kling_dispatch.py` consumed (NOT replaced).

### AC-7b.7-B â€” 9-node scaffold port-shape + Kling API live invocation

**Given** the canonical 9-node scaffold + Slab 2b.1 TEMPLATE pattern + Kling API client at `scripts/api_clients/kling_client.py`
**When** the dev-agent (Codex) authors Kira's Wave-3 port-shape
**Then** `app/specialists/kira/_act.py` lands with bounded body (â‰¤150 LOC AC-B ceiling) invoking `KlingClient.generate_motion(...)`
**And** `app/specialists/kira/graph.py` builds the 9-node scaffold (already established in Slab 2b era; refines body)
**And** `validate_scaffold("kira", build_kira_graph()).is_conforming is True`.

### AC-7b.7-C â€” Motion generation per `motion_plan.yaml` directive

**Given** Kira dispatched at G2F with a `motion_plan.yaml` directive in payload
**When** Kira generates motion per slide
**Then** per-slide `.progress.json` files land at `[BUNDLE_PATH]/motion/<slide_id>.progress.json` (intermediate; updated during generation)
**And** terminal `.json` receipts land at `[BUNDLE_PATH]/motion/<slide_id>.json` (final; carries `status: success|failure` + per-slide cost-tracking + provider response shape)
**And** reviewer inspection pack emitted at `[BUNDLE_PATH]/recovery/inspection/` (operator-readable forensics; one folder per failed slide).
**Test pin:** `tests/specialists/kira/test_kira_motion_generation.py` â€” VCR cassette; assert per-slide files emit + terminal receipts shape-correct.

### AC-7b.7-D â€” Fail-closed budget rules (NFR-CG20 binding)

**Given** the fail-closed budget rules per FR95 + NFR-CG20 rate-limit budget declaration
**When** Kira's per-slide motion budget is exceeded
**Then** Kira aborts cleanly with a terminal `.json` receipt carrying `status: "budget-exceeded"` + failure reason
**And** NO silent-degradation (NFR-CG20 binding); subsequent slides NOT attempted on budget exhaust
**And** failure path emits to `[BUNDLE_PATH]/recovery/inspection/<slide_id>/budget-exhausted.md`.
**Test pin:** `tests/specialists/kira/test_kira_fail_closed_budget.py` â€” VCR cassette with synthetic budget-exhaust response; assert clean abort.

### AC-7b.7-E â€” Live-API-on-CI strict prohibition (NFR-CG13)

**Given** NFR-CG13 strict prohibition
**When** the dev-agent (Codex) authors tests
**Then** `tests/specialists/kira/` use VCR cassettes under `tests/fixtures/specialist-replay/kira/`
**And** `scripts/utilities/detect_live_api_in_tests.py` AST-scan PASSES
**And** dev-agent ACs reference live-API only via shipped `httpx` + `kling_client.py` with `pytest.skip(...)`.

### AC-7b.7-F â€” Class-C 6-file BMB sanctum greenfield + SG-4 alignment

**Given** the SG-4 sanctum-alignment requirement + epic line 764 binding 6-file BMB at `_bmad/memory/bmad-agent-kira/` + `skills/bmad-agent-kling/SKILL.md` canonical
**When** the dev-agent authors Kira's sanctum
**Then** `_bmad/memory/bmad-agent-kira/` lands with 6-file BMB pattern (Class-C inheritance from 7b.6/Class-A precedent)
**And** `skills/bmad-agent-kling/SKILL.md` is verified option-a sanctum-aligned (minimal frontmatter; activation order references `bmad-agent-kira/`).

### AC-7b.7-G â€” FR105 per-specialist parity test (Class-C template inheritance)

**Given** the Class-C template active in validator from 7b.6 close
**When** the dev-agent (Codex) authors Kira's activation-contract test
**Then** `tests/parity/test_kira_activation_contract.py` (flat) lands inheriting `SanctumParityTestBase` with `class_template_id = "C"`, `specialist_name = "kira"`
**And** Class-C template assertions PASS (6-file BMB; Kling API binding; VCR cassettes; credential register; rate-limit budget; cold-activation smoke)
**And** `validate_parity_test_class_conformance.py` PASSES on this test file (NO new template extension needed; Class-C inherited from 7b.6).

### AC-7b.7-H â€” Cache-hit-rate N/A (Class-C inheritance from 7b.6)

**Given** Kira is REST-API tool-dispatch (no LLM at the Kira layer; same as Gary)
**When** the dev-agent considers FR106 wiring
**Then** **NO cache-hit-rate harness for Kira** â€” same rationale as 7b.6 (FR106 doesn't generalize to Class-C per Slab-2a-retrospective).

### AC-7b.7-I â€” Credential-rotation register (NFR-CG19) + rate-limit budget (NFR-CG20)

**Given** NFR-CG19 + NFR-CG20 requirements
**When** the dev-agent commits Kira port-shape
**Then** `state/config/credential-rotation-register.yaml` carries Kling API row (provider/owner/rotation_cadence/last_rotated/next_due/secret_store_reference)
**And** per-specialist rate-limit budget declared in `app/specialists/kira/config.yaml` (or model_config extension): `{rate_limit_per_minute, daily_budget_usd, per_invocation_cap_usd}`.

### AC-7b.7-J â€” Sandbox-AC governance + substrate-as-floor invariant

**Given** sandbox-AC + FR113 + NFR-I13
**When** validator runs
**Then** PASS; **no diff to `dispatch_adapter.py:70-95`**.

### AC-7b.7-K â€” Chain test inheriting `ChainTestBase`

**Given** NFR-CG14 + 7b.1 substrate
**When** the dev agent authors the Kira chain test
**Then** `tests/composition/test_kira_to_compositor_chain.py` lands inheriting `ChainTestBase` (Kira's motion artifacts feed Compositor at G3 â€” fixture-replay until 7b.11 lands; for Wave 3 dev, assert envelope-handoff shape only)
**And** wall-clock <120s.

### AC-7b.7-L â€” 7a.5 specialist-summary-writer integration

**Given** the 7a.5 conversation-persistence contract
**When** Kira `_act` completes
**Then** Kira invokes `summary_writer.emit_summary(specialist_id="kira", gate_id="G2F", payload=<verdict>)` per 7a.5 facade.

### AC-7b.7-M â€” Operator-gated AC-7-B (Completion Notes evidence)

**Given** the operator-gated AC-7-B requirement (NFR-T11b T5 live canary)
**When** the operator runs T5 live canary against real Kling API
**Then** â‰¤3 canary invocations; cost â‰¤$0.40 per canary
**And** evidence pasted into Completion Notes verbatim (API endpoint, request payload redacted, 200-OK response, motion artifact URL, cost).

### AC-7b.7-N â€” Close protocol

**Given** all prior ACs PASS + bmad-code-review PASS-or-PATCH-applied + regression baseline holds
**When** the story closes
**Then**:
  1. Sprint-status flip to `done`
  2. Wave-3 parallel close ledger entry (or amendment to wave_3_first_port_tripwire entry with 7b.7 contribution)
  3. next-session-start-here.md updated: pivot to 7b.8 Enrique close + 7b.9 Wanda Wave-4 open
  4. Deferred-inventory updates per drift resolutions
  5. SG-4 GREEN for Kira; Class-C template inheritance proven (NO new template extension)
  6. Three-line D12 close stub

---

## Tasks / Subtasks

### T1 â€” T1 readiness + gate-mode resolution + drift resolution
- [x] **T1.1** Round-(e) E3 verification + read 7b.6 close-verdict + apply gate-mode override if fired
- [x] **T1.2** 10-reading cascade
- [x] **T1.3** Wave-1/2a/2b closed + 7b.6 in review-or-done
- [x] **T1.4** Class-C template active verification
- [x] **T1.5** Kira current-state probe â€” 3 drifts
- [x] **T1.6** Drift resolution + gate-mode resolution recorded
- [x] **T1.7** Sandbox-AC validator pre-flight

### T2 â€” Kira sanctum greenfield 6-file BMB authoring + close drift follow-on
- [x] **T2.1** Author 6 BMB files at `_bmad/memory/bmad-agent-kira/`
- [x] **T2.2** Verify `skills/bmad-agent-kling/SKILL.md` minimal frontmatter + sanctum-aware activation order
- [x] **T2.3** Close `kira-sanctum-path-resolution` follow-on with verdict-specialist-name

### T3 â€” Kira `_act` body Wave-3 hardening (AC-B + AC-C + AC-D + AC-E)
- [x] **T3.1** Refine `app/specialists/kira/_act.py` â€” bounded body invoking `kling_client.py`
- [x] **T3.2** Wire motion generation per motion_plan.yaml; per-slide .progress.json + terminal .json receipts
- [x] **T3.3** Wire reviewer inspection pack emission at `[BUNDLE_PATH]/recovery/inspection/`
- [x] **T3.4** Wire fail-closed budget rules
- [x] **T3.5** Wire 7a.5 specialist-summary-writer (AC-L)
- [x] **T3.6** Consume legacy `kling_dispatch.py` as helper (NOT replace)
- [x] **T3.7** **AC-B 150-LOC ceiling discipline**

### T4 â€” VCR cassettes + sandbox-AC discipline (AC-E)
- [x] **T4.1** Author VCR cassettes at `tests/fixtures/specialist-replay/kira/`
- [x] **T4.2** `tests/specialists/kira/test_kira_motion_generation.py` (AC-C)
- [x] **T4.3** `tests/specialists/kira/test_kira_fail_closed_budget.py` (AC-D)
- [x] **T4.4** `tests/specialists/kira/test_kira_no_live_api_in_ci.py` â€” AST-scan PASS

### T5 â€” Parity + chain tests (AC-G + AC-K)
- [x] **T5.1** `tests/parity/test_kira_activation_contract.py` (flat; Class-C inherited template)
- [x] **T5.2** `tests/specialists/kira/test_kira_summary_landing.py` (AC-L)
- [x] **T5.3** `tests/composition/test_kira_to_compositor_chain.py` (AC-K)
- [x] **T5.4** Wall-clock annotations + validator PASS on Class-C

### T6 â€” Credential register + rate-limit budget (AC-I)
- [x] **T6.1** Kling row in `state/config/credential-rotation-register.yaml`
- [x] **T6.2** Rate-limit budget in `app/specialists/kira/config.yaml`

### T7 â€” SG-4 sanctum alignment verification
- [x] **T7.1** `tests/parity/test_skill_md_sanctum_alignment.py` PASSES for Kira

### T8 â€” Substrate-as-floor verification
- [x] **T8.1** `git diff` empty on dispatch_adapter.py:70-95

### T9 â€” Regression baseline + sandbox-AC final
- [x] **T9.1** Full regression battery
- [x] **T9.2** ruff story-scoped clean
- [x] **T9.3** lint-imports 9/9 KEPT
- [x] **T9.4** Sandbox-AC validator final PASS

### T10 â€” Codex G6 self-review
- [x] **T10.1** G6 self-review at `7b-7-codex-self-review-2026-04-XX.md`
- [x] **T10.2** Status flip `in-progress â†’ review`

### T11 â€” Claude bmad-code-review + close
- [x] **T11.1** `bmad-code-review` at `7b-7-code-review-2026-04-29.md`
- [x] **T11.2** Remediation cycle 1 applied: `KlingClient.generate_motion(...)` now polls terminal Kling result before Kira writes success receipts
- [x] **T11.3** Operator-gated AC-7-B not run; no operator canary window opened, remains operator-gated
- [x] **T11.4** Wave-3 parallel-close ledger entry
- [x] **T11.5** Sprint-status flip done
- [x] **T11.6** next-session-start-here.md update
- [x] **T11.7** Deferred-inventory updates
- [x] **T11.8** SG-4 GREEN for Kira
- [x] **T11.9** D12 close stub
- [x] **T11.10** Commit + push (sanctum gitignore force-add reminder)

### Review Findings
- [x] [Review][Patch] Kling terminal receipt was not terminal [`scripts/api_clients/kling_client.py`] â€” fixed in cycle 1 by adding `KlingClient.generate_motion(...)` submit-and-poll behavior and regression coverage.
- [x] [Review][Defer] Class-C validator method name remains provider-specific [`tests/parity/test_kira_activation_contract.py`] â€” deferred, already filed as `class-c-validator-method-name-provider-agnostic-rename`.

---

## Dev Notes

### Conditional gate-mode at story-open (Round-(e) E3 binding-hard)

This story's gate mode is determined by 7b.6 close-verdict, NOT pre-fixed. Sprint runner reads `tripwire_events::wave_3_first_port_tripwire::fired_verdict` at 7b.7 story-open:
- If `fired_verdict: false` â†’ 7b.7 opens single-gate (default per epic)
- If `fired_verdict: true` â†’ 7b.7 opens dual-gate (Round-(e) E3 binding-hard override)

Codex must record the resolved gate mode in T1.6 Drift Resolution block + Dev Agent Record.

### Class-C template inheritance from 7b.6 (NO new template extension)

7b.6 landed Class-C template; 7b.7 inherits without extension. The class-conformance validator already supports Class-C; Kira's parity test passes with `class_template_id = "C"`. NO lockstep validator extension needed (distinct from 7b.4/7b.5/7b.6 which each landed a new template).

### NFR predicates honored

NFR-T9 / T10 (VCR; â‰¤90s) / T11b (â‰¤3 canaries; â‰¤$0.40) / T12.
NFR-CG12 (sandbox-AC inventory `kling`) / CG13 (NO live-API in CI) / CG14 / CG16 / CG17 (Codex dev) / CG19 (credential register) / CG20 (rate-limit budget; fail-closed).
NFR-I9 + I10 + I12 (Class-C template inherited) + I13.

### Known follow-ons

- **`kira-sanctum-path-resolution`** â€” CLOSE at T2 with verdict-specialist-name
- **`bmad-memory-gitignore-force-add-policy`** â€” recurring; affects Kira sanctum at commit
- **`kira-7b-11-compositor-chain-test-fixture-replay`** â€” open; closes at 7b.11 Compositor close (Wave 5b) when real Compositor body lands

---

### Project Structure Notes

- `app/specialists/kira/` â€” already populated; this story REFINES `_act.py`, KEEPS `kling_dispatch.py`
- `_bmad/memory/bmad-agent-kira/` â€” NEW (sanctum greenfield; 6-file BMB Class-C pattern)
- `skills/bmad-agent-kling/` â€” UPDATED SKILL.md (canonical per epic Story 7b.7 line 764)
- `tests/parity/test_kira_activation_contract.py` â€” NEW (Class-C inherited template)
- `tests/specialists/kira/test_*.py` â€” NEW + UPDATED (4 behavioral tests)
- `tests/composition/test_kira_to_compositor_chain.py` â€” NEW (chain test)
- `tests/fixtures/specialist-replay/kira/` â€” NEW VCR cassettes
- `state/config/credential-rotation-register.yaml` â€” UPDATED (Kling row added)
- `app/specialists/kira/config.yaml` â€” NEW or EXTENDED (rate-limit budget)

---

## References

- **Round-(e) governance JSON**: [`docs/dev-guide/migration-story-governance.json`](../../docs/dev-guide/migration-story-governance.json) Â§`stories.7b-7` + Â§`stories.7b-6`
- **Epic + story-level scope**: [`epics-slab-7b-specialist-activation-eleven.md`](../planning-artifacts/epics-slab-7b-specialist-activation-eleven.md) Â§Story 7b.7
- **PRD FR95**: [`prd-slab-7b-specialist-activation-eleven.md`](../planning-artifacts/prd-slab-7b-specialist-activation-eleven.md) Â§FR95
- **Sandbox-AC inventory `kling` (FR107)**: [`docs/dev-guide/migration-ac-sandbox-inventory.json`](../../docs/dev-guide/migration-ac-sandbox-inventory.json) Â§`kling`
- **7b.6 Class-C precedent (immediate predecessor)**: [`migration-7b-6-gary-port-shape.md`](migration-7b-6-gary-port-shape.md)
- **Slab 2b.1 TEMPLATE**: [`migration-2b-1-gary-scaffold-migration.md`](migration-2b-1-gary-scaffold-migration.md)
- **Kling API client**: [`scripts/api_clients/kling_client.py`](../../scripts/api_clients/kling_client.py) + [`scripts/api_clients/kling_public_client.py`](../../scripts/api_clients/kling_public_client.py)
- **7b.1 substrate**: [`migration-7b-1-texas-hardening.md`](migration-7b-1-texas-hardening.md)
- **7a.5 conversation-persistence**: [`migration-7a-5-conversation-persistence-specialist-summary-writer.md`](migration-7a-5-conversation-persistence-specialist-summary-writer.md)
- **CLAUDE.md** governance

---

## Dev Agent Record

### Agent Model Used

GPT-5

### Debug Log References

- 2026-04-29 T1: Round-(e) E3 conditional gate override verified; 7b.6 is `done`; `wave_3_first_port_tripwire.fired_verdict=false`; Kira opens SINGLE-GATE.
- 2026-04-29 T1: Class-C template active preflight PASS (`validate_parity_test_class_conformance.py tests/parity/` reported 6 activation contracts before Kira, 7 after Kira).
- 2026-04-29 T1: Sandbox-AC preflight PASS; FR107 `kling` inventory entry present under current inventory shape (`dev_agent_available`).
- 2026-04-29 T3: Kira `_act()` body measured 23 LOC, below AC-B 150 LOC ceiling.
- 2026-04-29 T8: `git diff -- app/marcus/orchestrator/dispatch_adapter.py` empty.
- 2026-04-29 T9 focused battery: 55 passed.
- 2026-04-29 T9 broad regression: 1303 passed / 21 skipped / 1 deselected / 1 failed; the failure is known out-of-scope Wanda sanctum drift from the 7b.6 baseline.
- 2026-04-29 T9 utilities: pipeline lockstep PASS; live-API detector PASS; sandbox-AC PASS; Class-C conformance PASS; story-scoped ruff PASS; lint-imports 9/9 KEPT.
- 2026-04-29 T11 review: PASS-WITH-PATCH. PATCH-1 found Kira could mark a non-terminal Kling task-submission response as success; remediation added `KlingClient.generate_motion(...)` polling and regression coverage.
- 2026-04-29 T11 close verification: Kira/parity/composition + SG-4 + Kling API-client regression `60 passed` under `.venv`.

### Completion Notes List

- Gate-mode resolution: 7b.6 close verdict was available and `wave_3_first_port_tripwire.fired_verdict=false`; Kira opened SINGLE-GATE per Round-(e) E3 default.
- Drift #1 closed: Kira sanctum path is `_bmad/memory/bmad-agent-kira/` with six-file BMB pattern.
- Drift #2 closed: Class-C two-SKILL.md convention implemented. New persona skill at `skills/bmad-agent-kira/SKILL.md`; existing `skills/bmad-agent-kling/SKILL.md` preserved untouched as API-mastery reference material.
- Drift #3 acknowledged: legacy `app/specialists/kira/kling_dispatch.py` remains in place and is consumed by `_act.py` as a helper.
- Kira `_act.py` emits per-slide `.progress.json` and terminal `.json` receipts under `[BUNDLE_PATH]/motion/`, writes failure/budget inspection notes under `[BUNDLE_PATH]/recovery/inspection/`, and aborts cleanly on budget exhaustion before subsequent slides.
- T11 remediation hardened terminal receipt semantics: the shipped `KlingClient.generate_motion(...)` path now submits motion jobs and waits for completion before Kira records a success video URL.
- NFR-CG19/CG20 landed: Kling credential register row plus `app/specialists/kira/config.yaml` rate-limit budget.
- 7a.5 summary facade wired with `specialist_id="kira"` and `gate_id="G2F"`.
- AC-7-B live Kling canary was not run by Codex; remains operator-gated for T11 close notes if an operator window opens.
- D12 close stub: 7b.7 closed done; SG-4 GREEN for Kira; Wave-3 next remains 7b.8 Enrique then 7b.9 Wanda.

### File List

- `_bmad/memory/bmad-agent-kira/INDEX.md`
- `_bmad/memory/bmad-agent-kira/PERSONA.md`
- `_bmad/memory/bmad-agent-kira/CREED.md`
- `_bmad/memory/bmad-agent-kira/BOND.md`
- `_bmad/memory/bmad-agent-kira/MEMORY.md`
- `_bmad/memory/bmad-agent-kira/CAPABILITIES.md`
- `_bmad-output/implementation-artifacts/7b-7-codex-self-review-2026-04-29.md`
- `_bmad-output/implementation-artifacts/migration-7b-7-kira-port-shape.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `app/specialists/kira/_act.py`
- `app/specialists/kira/config.yaml`
- `app/specialists/kira/graph.py`
- `app/specialists/kira/model_config.yaml`
- `scripts/api_clients/kling_client.py`
- `scripts/utilities/detect_live_api_in_tests.py`
- `skills/bmad-agent-kira/SKILL.md`
- `state/config/credential-rotation-register.yaml`
- `tests/composition/test_kira_to_compositor_chain.py`
- `tests/fixtures/composition/kira-to-compositor/expected-output.yaml`
- `tests/fixtures/specialist-replay/kira/kling_motion_happy_path.yaml`
- `tests/fixtures/specialist-replay/kira/kling_budget_exhaust.yaml`
- `tests/parity/test_kira_activation_contract.py`
- `tests/parity/test_skill_md_sanctum_alignment.py`
- `tests/test_kling_client_polling.py`
- `tests/specialists/kira/test_kira_act_node_llm_invocation.py`
- `tests/specialists/kira/test_kira_fail_closed_budget.py`
- `tests/specialists/kira/test_kira_motion_generation.py`
- `tests/specialists/kira/test_kira_no_live_api_in_ci.py`
- `tests/specialists/kira/test_kira_storyboard_contract.py`
- `tests/specialists/kira/test_kira_summary_landing.py`
