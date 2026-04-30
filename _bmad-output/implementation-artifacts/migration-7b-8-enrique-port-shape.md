# Migration Story 7b.8: Enrique Port-Shape — ElevenLabs API + Voice-Selection HIL Contract

**Status:** done
**Sprint key:** `migration-7b-8-enrique-port-shape`
**Epic:** Slab 7b Specialist Body Activation — `epic-slab-7b-specialist-activation-eleven`. **Wave 3 parallel** (Class-C API-bound; PARALLEL with 7b.6 Gary + 7b.7 Kira; Claude-authored spec / Codex dev per NFR-CG17 + D21).
**Pts:** 4 | **Gate:** **single (DEFAULT) → dual (CONDITIONAL via Round-(e) E3 binding-hard `conditional_gate_override` keyed to 7b.6 first-port tripwire)** | **K-target:** ~1.4× (target ~33 tests / floor ~25; ~2.9K LOC).
**Author:** **Claude** spec / **Codex** dev. **Review:** **Claude** T11 `bmad-code-review`.
**Wave-3 precondition:** 7b.6 (Gary first-port) opens (parallel; not strict-after); BUT Round-(e) E3 binding-hard requires sprint runner to read 7b.6 close-verdict at this story's open AND apply gate-mode override if 7b.6 first-port tripwire fired (>2.7K LOC). **Note: `enrique` ↔ `elevenlabs` aliasing per `app/manifest/compiler.py::SPECIALIST_ALIASES`.**

---

## Round-(e) Governance Inheritance

Round-(e) freeze landed 2026-04-29. Load-bearing for 7b.8:

- **E3 binding-hard `conditional_gate_override`:** trigger_story = 7b-6; trigger_condition = 7b-6 closes >2.7K LOC; override_gate_mode = dual-gate; binding=hard. Sprint runner MUST read `tripwire_escalation_record_path` at 7b.8 story-open and apply override if fired.

**T1 readiness verification command:**
```bash
.venv/Scripts/python.exe -c "import json; d = json.load(open('docs/dev-guide/migration-story-governance.json', encoding='utf-8')); entry = d['stories']['7b-8']['conditional_gate_override']; assert entry['trigger_story'] == '7b-6'; assert entry['override_gate_mode'] == 'dual-gate'; assert entry['binding'] == 'hard'; print('Round-(e) E3 conditional_gate_override verified PASS for 7b-8')"
```

Then read tripwire ledger at story-open (mirror 7b.7 pattern):
```bash
.venv/Scripts/python.exe -c "
import yaml
d = yaml.safe_load(open('_bmad-output/implementation-artifacts/sprint-status.yaml', encoding='utf-8'))
events = [e for e in d.get('tripwire_events', []) if e.get('tripwire_id') == 'wave_3_first_port_tripwire']
if not events: print('7b-6 not yet closed; HALT 7b-8 dev open')
elif events[-1]['fired_verdict'] in (True, 'true'): print('TRIPWIRE FIRED → 7b-8 OPENS DUAL-GATE')
else: print('TRIPWIRE NOT FIRED → 7b-8 OPENS SINGLE-GATE')
"
```

---

## T1 Readiness Block

### Required-readings cascade (10-reading)

1. **Round-(e) governance JSON** — `docs/dev-guide/migration-story-governance.json` §`stories.7b-8` + §`stories.7b-6` + tripwire ledger.
2. **Epic + story-level scope** — [`epics-slab-7b-specialist-activation-eleven.md`](../planning-artifacts/epics-slab-7b-specialist-activation-eleven.md) §Story 7b.8 (lines 787-834).
3. **PRD §FR97** — ElevenLabs API live invocation + voice-preview/voice-selection HIL contract (`voice-preview-options.json` + `voice-selection-review.md` + `voice-selection.json` artifact write) + manifest-driven narration on locked package + assembly-bundle build (`assembly-bundle/audio/` + `captions/`) + per-segment progress to stderr.
4. **Sandbox-AC inventory entry `elevenlabs` (FR107; Wave 0 LANDED)** — [`docs/dev-guide/migration-ac-sandbox-inventory.json`](../../docs/dev-guide/migration-ac-sandbox-inventory.json) §`elevenlabs`.
5. **7b.6 Gary Class-C precedent (Wave-3 first-port)** — [`migration-7b-6-gary-port-shape.md`](migration-7b-6-gary-port-shape.md). Inherit Class-C template + 6-file BMB + VCR cassettes + NFR-CG13/19/20 + operator-gated AC-N-B.
6. **7b.7 Kira parallel sibling (mirror conditional_gate_override pattern)** — [`migration-7b-7-kira-port-shape.md`](migration-7b-7-kira-port-shape.md). Same Round-(e) E3 conditional-gate-override discipline.
7. **Slab 2b.1 TEMPLATE** — [`migration-2b-1-gary-scaffold-migration.md`](migration-2b-1-gary-scaffold-migration.md).
8. **Specialist migration template (R1-R14)** — [`docs/dev-guide/specialist-migration-template.md`](../../docs/dev-guide/specialist-migration-template.md).
9. **`scripts/api_clients/elevenlabs_client.py`** — ElevenLabs API client (already shipped; Slab 2b.x era).
10. **CLAUDE.md** — §LangChain/LangGraph migration governance + NFR-CG13/19/20 + `enrique` ↔ `elevenlabs` SPECIALIST_ALIASES handling.

### Enrique current-state probe + drift surfacing

```bash
ls app/specialists/enrique/                        # __init__.py expertise/ elevenlabs_dispatch.py graph.py model_config.yaml state.py (Slab 2b era)
ls _bmad/memory/bmad-agent-enrique/ 2>/dev/null    # NOT YET PRESENT — sanctum greenfield (Slab 7b convention)
ls _bmad/memory/bmad-agent-elevenlabs/ 2>/dev/null # NOT YET PRESENT either — Slab 2b.1 era expected this path but never populated
ls skills/bmad-agent-elevenlabs/                   # SKILL.md + references/ (skill-dir uses elevenlabs per A11 pattern)
ls skills/bmad-agent-enrique/ 2>/dev/null          # may or may not exist
ls scripts/api_clients/elevenlabs_client.py
```

**Three drifts surface at T1 (mirror 7b.6 + 7b.7):**

**⚠️ Drift #1 — Sanctum dir path: skill-dir-name (`bmad-agent-elevenlabs/`) vs Slab 7b epic (`bmad-agent-enrique/`):** Same A11 pattern. **Resolution at T1 (binding):** path = `_bmad/memory/bmad-agent-enrique/` per Slab 7b specialist-name convention. Filed as deferred-inventory follow-on `enrique-sanctum-path-resolution` — CLOSED at this story T2.

**⚠️ Drift #2 — Class-C two-SKILL.md convention (party-mode-ratified 2026-04-29 binding):** Per Round-(f) party-mode 4/4 unanimous on option (a) ratified post-7b.6 close: Class-C specialists use TWO SKILL.md files — persona-skill at specialist-name path + API-mastery preserved at API-name path. **Resolution at T1 (binding):**
- **CREATE** `skills/bmad-agent-enrique/SKILL.md` (NEW persona-skill; minimal FR101 R1 frontmatter `name: bmad-agent-enrique` + persona-focused description; body = activation hot-load batch referencing `_bmad/memory/bmad-agent-enrique/` BMB sanctum). Mirrors 7b.6 Gary pattern.
- **PRESERVE** `skills/bmad-agent-elevenlabs/SKILL.md` UNTOUCHED — Slab 2b.x era ElevenLabs API-mastery skill; consumed lazily as API reference (line in NEW enrique/SKILL.md says "Use `skills/bmad-agent-elevenlabs/` only as ElevenLabs API reference material; runtime execution via `app/specialists/enrique/`").
- Filed as deferred-inventory follow-on `class-c-two-skill-md-convention-ratified` — closed cumulatively across Wave-3+4 stories.

**⚠️ Drift #3 — Existing `elevenlabs_dispatch.py` legacy at `app/specialists/enrique/`:** Slab-2b era carry-forward; consume (NOT replace) per substrate-as-floor.

### Wave 0 + 7b.1 substrate + Wave 1/2a/2b/3-first-port sweeps

```bash
# Wave 0 + 7b.1 substrate
ls docs/dev-guide/bmb-sanctum-alignment-checklist.md docs/dev-guide/sanctum-exception-categories.json docs/dev-guide/operator-control-parity-template.md docs/dev-guide/migration-ac-sandbox-inventory.json skills/bmad-agent-cora/SKILL.md
ls tests/parity/_sanctum_parity_base.py tests/composition/_chain_test_base.py scripts/utilities/validate_parity_test_class_conformance.py

# Waves 1+2a+2b closed; 7b.6 in review-or-done (parallel; not strict-after)
.venv/Scripts/python.exe -c "
import yaml
d = yaml.safe_load(open('_bmad-output/implementation-artifacts/sprint-status.yaml', encoding='utf-8'))
done = lambda k: d['development_status'][k].startswith('done')
in_review_or_done = lambda k: d['development_status'][k].startswith(('done', 'review'))
assert all(done(k) for k in ('migration-7b-1-texas-hardening','migration-7b-2-quinn-r-hardening','migration-7b-3-vera-hardening','migration-7b-4-irene-pass1-refresh','migration-7b-5-tracy-port-shape-sidecar'))
assert in_review_or_done('migration-7b-6-gary-port-shape'), '7b-6 must be in review or done before 7b-8 opens (need fired_verdict)'
print('Wave-3 first-port verdict available')
"

# FR107 sandbox-AC `elevenlabs` entry present
.venv/Scripts/python.exe -c "import json; d = json.load(open('docs/dev-guide/migration-ac-sandbox-inventory.json', encoding='utf-8')); assert 'elevenlabs' in d['notes']; print('elevenlabs entry present')"

# Class-C template active (from 7b.6)
.venv/Scripts/python.exe scripts/utilities/validate_parity_test_class_conformance.py tests/parity/  # PASS expected
```

### Sandbox-AC validator pre-flight

```bash
.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py \
  _bmad-output/implementation-artifacts/migration-7b-8-enrique-port-shape.md
```
Expect PASS. All ElevenLabs API verification wraps via shipped `httpx` + `elevenlabs_client.py` with `pytest.skip(...)`.

### Standing pre-flight items

1-3. Standard (severance posture; substrate-frozen; NFR-T9-T12).
4. **Conditional gate-mode at story-open** per Round-(e) E3.
5. `enrique` ↔ `elevenlabs` SPECIALIST_ALIASES — per `app/manifest/compiler.py:43-46` carry-forward; specialist_id mapping enforced in summary writer + dispatch registry.

---

## Story

As a **migration dev agent**,
I want **Enrique to execute a Class-C port-shape — ElevenLabs API live invocation via `elevenlabs_client.py` + voice-preview/voice-selection HIL contract (emitting `voice-preview-options.json`, operator reviews via `voice-selection-review.md`, operator selection lands in `voice-selection.json`) + manifest-driven narration on locked package + assembly-bundle build (`assembly-bundle/audio/` + `captions/`) + per-segment progress to stderr — AND I want Enrique's sanctum greenfield at `_bmad/memory/bmad-agent-enrique/` (6-file BMB Class-C pattern) per inheritance from 7b.6**,
So that **(a) Trial-2 reaches G2 with real Enrique narration audio + captions and the operator selects the voice via the HIL contract (not silent default), (b) the voice-selection HIL artifact-set is operator-actionable, (c) manifest-driven narration runs against the locked package (Pass-1 scope-locked + Pass-2 enriched), and (d) SG-4 enforced via Class-C template inheritance**.

---

## Acceptance Criteria

All ACs are dev-agent-executable (sandbox-AC compliant). Live-API via `httpx` + `elevenlabs_client.py` with `pytest.skip(...)`; live canary deferred to operator-gated AC-8-B Completion-Notes.

### AC-7b.8-A — T1 readiness + gate-mode resolution + drift resolution

**Given** Round-(e) E3 binding-hard + Wave-3 first-port (7b.6) close-verdict known
**When** the dev agent runs T1 readiness
**Then** all 10 readings cascade complete; tripwire ledger read; gate-mode resolved (single OR dual per 7b.6 verdict)
**And** Drift #1 resolution recorded: sanctum path = `_bmad/memory/bmad-agent-enrique/`
**And** Drift #2 resolution recorded: SKILL.md canonical = `skills/bmad-agent-elevenlabs/SKILL.md`
**And** Drift #3 acknowledged: legacy `elevenlabs_dispatch.py` consumed (NOT replaced).

### AC-7b.8-B — 9-node scaffold port-shape + ElevenLabs API live invocation

**Given** Slab 2b.1 TEMPLATE pattern + ElevenLabs API client
**When** the dev-agent (Codex) authors Enrique's Wave-3 port-shape
**Then** `app/specialists/enrique/_act.py` lands with bounded body (≤150 LOC AC-B ceiling) invoking `ElevenLabsClient` from `elevenlabs_client.py`
**And** `app/specialists/enrique/graph.py` builds the 9-node scaffold (existing Slab 2b era; refines body)
**And** `validate_scaffold("enrique", build_enrique_graph()).is_conforming is True`.

### AC-7b.8-C — Voice-preview / voice-selection HIL contract (FR97 primary)

**Given** Enrique dispatched at G2 voice-preview phase
**When** Enrique runs voice-preview
**Then** `voice-preview-options.json` is emitted at `[BUNDLE_PATH]/voice-selection/voice-preview-options.json` carrying N candidate voices per the run-constants (`{voices: [{voice_id, voice_name, sample_audio_url, characteristics: {...}, eta_seconds, cost_per_1k_chars}]}`)
**And** the operator reviews via `voice-selection-review.md` (markdown viewer; emitted at `[BUNDLE_PATH]/voice-selection/voice-selection-review.md`; one-line-per-voice + recommended-voice marker)
**And** the operator's selection lands in `voice-selection.json` at `[BUNDLE_PATH]/voice-selection/voice-selection.json` per FR97 contract (`{selected_voice_id, selected_at, operator_id, rationale}`).
**Test pin:** `tests/specialists/enrique/test_enrique_voice_selection_hil.py` — VCR cassette; assert artifact emission shape; parametrize over operator-selected vs operator-defaulted-recommended.

### AC-7b.8-D — Manifest-driven narration on locked package

**Given** Enrique dispatched post-voice-selection with locked Pass-2 narration script
**When** Enrique generates narration per the storyboard's locked manifest
**Then** narration audio per segment lands at `[BUNDLE_PATH]/assembly-bundle/audio/<segment_id>.mp3` (or .wav per provider)
**And** captions land at `[BUNDLE_PATH]/assembly-bundle/captions/<segment_id>.vtt`
**And** per-segment progress emitted to stderr (`Enrique segment <segment_id> [N/total] OK | duration=<s>s | cost=<usd>`).
**Test pin:** `tests/specialists/enrique/test_enrique_assembly_bundle_build.py` — VCR cassette; assert `assembly-bundle/audio/` + `captions/` populated + per-segment progress captured.

### AC-7b.8-E — Live-API-on-CI strict prohibition (NFR-CG13)

**Given** NFR-CG13 strict prohibition
**When** the dev-agent (Codex) authors tests
**Then** `tests/specialists/enrique/` use VCR cassettes under `tests/fixtures/specialist-replay/enrique/`
**And** `scripts/utilities/detect_live_api_in_tests.py` AST-scan PASSES
**And** dev-agent ACs reference live-API only via shipped `httpx` + `elevenlabs_client.py` with `pytest.skip(...)`.

### AC-7b.8-F — Class-C 6-file BMB sanctum greenfield + SG-4 alignment

**Given** SG-4 + epic line 819 binding 6-file BMB at `_bmad/memory/bmad-agent-enrique/` + `skills/bmad-agent-elevenlabs/SKILL.md` canonical
**When** the dev-agent authors Enrique's sanctum
**Then** `_bmad/memory/bmad-agent-enrique/` lands with 6-file BMB pattern (Class-C inheritance from 7b.6/Class-A)
**And** `skills/bmad-agent-elevenlabs/SKILL.md` minimal frontmatter + activation-order references `bmad-agent-enrique/`.

### AC-7b.8-G — FR105 per-specialist parity test (Class-C template inheritance)

**Given** Class-C template active in validator from 7b.6 close
**When** the dev-agent authors Enrique's activation-contract test
**Then** `tests/parity/test_enrique_activation_contract.py` (flat) lands inheriting `SanctumParityTestBase` with `class_template_id = "C"`, `specialist_name = "enrique"`
**And** Class-C template assertions PASS + voice-selection HIL contract write parity (extension assertion specific to Enrique; documented in test as per-story Class-C-specific extension)
**And** `validate_parity_test_class_conformance.py` PASSES (NO new template extension; Class-C inherited from 7b.6).

### AC-7b.8-H — Cache-hit-rate N/A (Class-C inheritance)

**Given** Enrique is REST-API tool-dispatch (no LLM at the Enrique layer)
**Then** **NO cache-hit-rate harness for Enrique** — same rationale as Gary/Kira (FR106 doesn't generalize to Class-C).

### AC-7b.8-I — Credential-rotation register (NFR-CG19) + rate-limit budget (NFR-CG20)

**Given** NFR-CG19 + NFR-CG20
**When** the dev-agent commits Enrique port-shape
**Then** `state/config/credential-rotation-register.yaml` carries ElevenLabs row
**And** per-specialist rate-limit budget declared in `app/specialists/enrique/config.yaml`.

### AC-7b.8-J — Sandbox-AC governance + substrate-as-floor invariant

**Given** sandbox-AC + FR113 + NFR-I13
**When** validator runs
**Then** PASS; **no diff to `dispatch_adapter.py:70-95`**.

### AC-7b.8-K — Chain test inheriting `ChainTestBase`

**Given** NFR-CG14 + 7b.1 substrate
**When** the dev agent authors the Enrique chain test
**Then** `tests/composition/test_enrique_to_compositor_chain.py` lands inheriting `ChainTestBase` (Enrique's audio + captions feed Compositor at G3 — fixture-replay until 7b.11 lands)
**And** wall-clock <120s.

### AC-7b.8-L — 7a.5 specialist-summary-writer integration

**Given** the 7a.5 conversation-persistence contract + `enrique`/`elevenlabs` specialist_id aliasing
**When** Enrique `_act` completes
**Then** Enrique invokes `summary_writer.emit_summary(specialist_id="enrique", gate_id="G2", ...)` per 7a.5 facade
**And** the summary respects `app/manifest/compiler.py::SPECIALIST_ALIASES["elevenlabs": "enrique"]` mapping.

### AC-7b.8-M — Operator-gated AC-8-B (Completion Notes evidence)

**Given** operator-gated AC-8-B (NFR-T11b T5 live canary)
**When** the operator runs T5 live canary against real ElevenLabs API
**Then** ≤3 canary invocations; cost ≤$0.40 per canary
**And** evidence pasted into Completion Notes: API endpoint, request payload (redacted), 200-OK + audio sample URL + captions, cost.

### AC-7b.8-N — Close protocol

**Given** all prior ACs PASS + bmad-code-review PASS-or-PATCH-applied + regression baseline holds
**When** the story closes
**Then**:
  1. Sprint-status flip `done`
  2. Wave-3 parallel close ledger entry (alongside 7b.6 + 7b.7 entries)
  3. next-session-start-here.md update: pivot to Wave 4 (7b.9 Wanda) opening
  4. Deferred-inventory updates per drift resolutions
  5. SG-4 GREEN for Enrique; Class-C template inheritance proven (no new extension)
  6. Three-line D12 close stub

---

## Tasks / Subtasks

### T1 — T1 readiness + gate-mode resolution + drift resolution
- [x] **T1.1** Round-(e) E3 verification + 7b.6 close-verdict + gate-mode override if fired
- [x] **T1.2** 10-reading cascade
- [x] **T1.3** Wave-1/2a/2b closed + 7b.6 in review-or-done
- [x] **T1.4** Class-C template active verification
- [x] **T1.5** Enrique current-state probe — 3 drifts
- [x] **T1.6** Drift + gate-mode resolution recorded
- [x] **T1.7** Sandbox-AC validator pre-flight

### T2 — Enrique sanctum greenfield 6-file BMB authoring
- [x] **T2.1** Author 6 BMB files at `_bmad/memory/bmad-agent-enrique/`
- [x] **T2.2** `skills/bmad-agent-elevenlabs/SKILL.md` minimal frontmatter + sanctum-aware activation order
- [x] **T2.3** Close `enrique-sanctum-path-resolution` follow-on with verdict-specialist-name

### T3 — Enrique `_act` body Wave-3 hardening
- [x] **T3.1** Refine `app/specialists/enrique/_act.py` — bounded body invoking `elevenlabs_client.py`
- [x] **T3.2** Wire voice-preview/voice-selection HIL contract (3 artifacts)
- [x] **T3.3** Wire manifest-driven narration + assembly-bundle build (`audio/` + `captions/`)
- [x] **T3.4** Wire per-segment progress to stderr
- [x] **T3.5** Wire 7a.5 specialist-summary-writer (AC-L)
- [x] **T3.6** Consume legacy `elevenlabs_dispatch.py` as helper
- [x] **T3.7** **AC-B 150-LOC ceiling discipline**

### T4 — VCR cassettes + sandbox-AC discipline
- [x] **T4.1** VCR cassettes at `tests/fixtures/specialist-replay/enrique/`
- [x] **T4.2** `tests/specialists/enrique/test_enrique_voice_selection_hil.py` (AC-C)
- [x] **T4.3** `tests/specialists/enrique/test_enrique_assembly_bundle_build.py` (AC-D)
- [x] **T4.4** `tests/specialists/enrique/test_enrique_no_live_api_in_ci.py` — AST-scan PASS

### T5 — Parity + chain tests
- [x] **T5.1** `tests/parity/test_enrique_activation_contract.py` (flat; Class-C inherited template)
- [x] **T5.2** `tests/specialists/enrique/test_enrique_summary_landing.py` (AC-L; verifies elevenlabs/enrique aliasing)
- [x] **T5.3** `tests/composition/test_enrique_to_compositor_chain.py` (AC-K)
- [x] **T5.4** Wall-clock annotations + validator PASS on Class-C

### T6 — Credential register + rate-limit budget
- [x] **T6.1** ElevenLabs row in `state/config/credential-rotation-register.yaml`
- [x] **T6.2** Rate-limit budget in `app/specialists/enrique/config.yaml`

### T7 — SG-4 sanctum alignment verification
- [x] **T7.1** `tests/parity/test_skill_md_sanctum_alignment.py` PASSES for Enrique

### T8 — Substrate-as-floor verification
- [x] **T8.1** `git diff` empty on dispatch_adapter.py:70-95

### T9 — Regression baseline + sandbox-AC final
- [x] **T9.1** Full regression battery
- [x] **T9.2-T9.4** ruff/lint-imports/sandbox-AC final

### T10 — Codex G6 self-review
- [x] **T10.1** G6 self-review at `7b-8-codex-self-review-2026-04-XX.md`
- [x] **T10.2** Status flip `in-progress → review`

### T11 — Claude bmad-code-review + close
- [ ] **T11.1** `bmad-code-review` at `7b-8-code-review-2026-04-XX.md`
- [ ] **T11.2** Remediation cycle 1 if needed
- [ ] **T11.3** Operator-gated AC-8-B if window opens
- [ ] **T11.4** Wave-3 parallel-close ledger amendment
- [ ] **T11.5** Sprint-status flip done
- [ ] **T11.6** next-session-start-here.md update
- [ ] **T11.7** Deferred-inventory updates
- [ ] **T11.8** SG-4 GREEN for Enrique
- [ ] **T11.9** D12 close stub
- [ ] **T11.10** Commit + push (force-add gitignored sanctum)

---

## Dev Notes

### Conditional gate-mode at story-open (Round-(e) E3 binding-hard)

Same pattern as 7b.7 Kira. Sprint runner reads `wave_3_first_port_tripwire::fired_verdict` at 7b.8 story-open; applies dual-gate override if fired. Codex records resolved gate mode in T1.6 + Dev Agent Record.

### Class-C template inheritance from 7b.6 (NO new template extension)

7b.6 landed Class-C template; 7b.7 + 7b.8 inherit without extension. Enrique's voice-selection HIL contract is a per-story Class-C extension assertion (documented in test); does NOT extend the validator.

### `enrique` ↔ `elevenlabs` aliasing

Per `app/manifest/compiler.py::SPECIALIST_ALIASES`, the manifest-side alias is `elevenlabs`; runtime persona / specialist_id is `enrique`. Summary writer + dispatch registry + tests must respect both forms. AC-L explicitly verifies aliasing.

### NFR predicates honored

NFR-T9 / T10 (VCR; ≤90s) / T11b (≤3 canaries; ≤$0.40) / T12.
NFR-CG12 (sandbox-AC inventory `elevenlabs`) / CG13 (NO live-API in CI) / CG14 / CG16 / CG17 (Codex dev) / CG19 (credential register) / CG20 (rate-limit budget).
NFR-I9 + I10 + I12 (Class-C template inherited) + I13.

### Known follow-ons

- **`enrique-sanctum-path-resolution`** — CLOSE at T2 with verdict-specialist-name
- **`bmad-memory-gitignore-force-add-policy`** — recurring; affects Enrique sanctum at commit
- **`enrique-7b-11-compositor-chain-test-fixture-replay`** — open; closes at 7b.11

---

### Project Structure Notes

- `app/specialists/enrique/` — already populated; this story REFINES `_act.py`, KEEPS `elevenlabs_dispatch.py`
- `_bmad/memory/bmad-agent-enrique/` — NEW (sanctum greenfield; 6-file BMB Class-C)
- `skills/bmad-agent-elevenlabs/` — UPDATED SKILL.md (canonical per epic line 819)
- `tests/parity/test_enrique_activation_contract.py` — NEW
- `tests/specialists/enrique/test_*.py` — NEW + UPDATED (4 behavioral tests)
- `tests/composition/test_enrique_to_compositor_chain.py` — NEW
- `tests/fixtures/specialist-replay/enrique/` — NEW VCR cassettes
- `state/config/credential-rotation-register.yaml` — UPDATED (ElevenLabs row)
- `app/specialists/enrique/config.yaml` — NEW (rate-limit budget)

---

## References

- **Round-(e) governance JSON**: [`docs/dev-guide/migration-story-governance.json`](../../docs/dev-guide/migration-story-governance.json) §`stories.7b-8` + §`stories.7b-6`
- **Epic + story-level scope**: [`epics-slab-7b-specialist-activation-eleven.md`](../planning-artifacts/epics-slab-7b-specialist-activation-eleven.md) §Story 7b.8
- **PRD FR97**: [`prd-slab-7b-specialist-activation-eleven.md`](../planning-artifacts/prd-slab-7b-specialist-activation-eleven.md) §FR97
- **Sandbox-AC inventory `elevenlabs` (FR107)**: [`docs/dev-guide/migration-ac-sandbox-inventory.json`](../../docs/dev-guide/migration-ac-sandbox-inventory.json) §`elevenlabs`
- **7b.6 Gary Class-C precedent**: [`migration-7b-6-gary-port-shape.md`](migration-7b-6-gary-port-shape.md)
- **7b.7 Kira parallel sibling**: [`migration-7b-7-kira-port-shape.md`](migration-7b-7-kira-port-shape.md)
- **Slab 2b.1 TEMPLATE**: [`migration-2b-1-gary-scaffold-migration.md`](migration-2b-1-gary-scaffold-migration.md)
- **ElevenLabs API client**: [`scripts/api_clients/elevenlabs_client.py`](../../scripts/api_clients/elevenlabs_client.py)
- **7b.1 substrate**: [`migration-7b-1-texas-hardening.md`](migration-7b-1-texas-hardening.md)
- **7a.5 conversation-persistence**: [`migration-7a-5-conversation-persistence-specialist-summary-writer.md`](migration-7a-5-conversation-persistence-specialist-summary-writer.md)
- **CLAUDE.md** governance + SPECIALIST_ALIASES handling

---

## Dev Agent Record

### Agent Model Used

GPT-5

### Debug Log References

- 2026-04-29 T1: Round-(e) E3 conditional gate override verified; 7b.6 is `done`; `wave_3_first_port_tripwire.fired_verdict=false`; 7b.7 treated closed per operator instruction and sprint ledger; Enrique opens SINGLE-GATE.
- 2026-04-29 T1: Class-C template preflight PASS (`validate_parity_test_class_conformance.py tests/parity/` reported 7 activation contracts before Enrique, 8 after Enrique).
- 2026-04-29 T1: Sandbox-AC preflight PASS; FR107 `elevenlabs` inventory entry present.
- 2026-04-29 T3: Enrique `_act.act()` body measured 20 logical LOC, below AC-B 150 LOC ceiling.
- 2026-04-29 T8: `git diff -- app/marcus/orchestrator/dispatch_adapter.py` empty.
- 2026-04-29 T9 focused battery: 61 passed.
- 2026-04-29 T9 broad regression: 1315 passed / 21 skipped / 1 deselected / 1 failed; the failure is known out-of-scope Wanda sanctum drift from prior Wave-3 baseline.
- 2026-04-29 T9 utilities: pipeline lockstep PASS; live-API detector PASS; sandbox-AC PASS; Class-C conformance PASS; story-scoped ruff PASS; lint-imports 9/9 KEPT.

### Completion Notes List

- Gate-mode resolution: 7b.6 close verdict was available and `wave_3_first_port_tripwire.fired_verdict=false`; Enrique opened SINGLE-GATE per Round-(e) E3 default.
- Drift #1 closed: Enrique sanctum path is `_bmad/memory/bmad-agent-enrique/` with six-file BMB pattern.
- Drift #2 closed per ratified Class-C two-SKILL.md convention: new persona skill at `skills/bmad-agent-enrique/SKILL.md`; existing `skills/bmad-agent-elevenlabs/SKILL.md` preserved untouched as API-mastery reference material.
- Drift #3 acknowledged: legacy `app/specialists/enrique/elevenlabs_dispatch.py` remains in place and is consumed as helper/reference surface.
- Enrique `_act.py` emits the voice-selection HIL artifact trio, writes per-segment audio/captions under `assembly-bundle/`, emits per-segment stderr progress, and builds a Compositor handoff shape.
- NFR-CG19/CG20 landed: ElevenLabs credential register row plus `app/specialists/enrique/config.yaml` rate-limit budget.
- 7a.5 summary facade wired with `specialist_id="enrique"` and `gate_id="G2"`; tests verify `elevenlabs` aliases to `enrique`.
- AC-8-B live ElevenLabs canary was not run by Codex; remains operator-gated for T11 close notes if an operator window opens.

### File List

- `_bmad/memory/bmad-agent-enrique/INDEX.md`
- `_bmad/memory/bmad-agent-enrique/PERSONA.md`
- `_bmad/memory/bmad-agent-enrique/CREED.md`
- `_bmad/memory/bmad-agent-enrique/BOND.md`
- `_bmad/memory/bmad-agent-enrique/MEMORY.md`
- `_bmad/memory/bmad-agent-enrique/CAPABILITIES.md`
- `_bmad-output/implementation-artifacts/7b-8-codex-self-review-2026-04-29.md`
- `_bmad-output/implementation-artifacts/migration-7b-8-enrique-port-shape.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `app/specialists/enrique/_act.py`
- `app/specialists/enrique/config.yaml`
- `app/specialists/enrique/graph.py`
- `app/specialists/enrique/model_config.yaml`
- `scripts/utilities/detect_live_api_in_tests.py`
- `skills/bmad-agent-enrique/SKILL.md`
- `state/config/credential-rotation-register.yaml`
- `tests/composition/test_enrique_to_compositor_chain.py`
- `tests/fixtures/composition/enrique-to-compositor/expected-output.yaml`
- `tests/fixtures/specialist-replay/enrique/elevenlabs_voice_preview.yaml`
- `tests/fixtures/specialist-replay/enrique/elevenlabs_narration_happy_path.yaml`
- `tests/parity/test_enrique_activation_contract.py`
- `tests/parity/test_skill_md_sanctum_alignment.py`
- `tests/specialists/enrique/test_enrique_act_node_dispatch.py`
- `tests/specialists/enrique/test_enrique_assembly_bundle_build.py`
- `tests/specialists/enrique/test_enrique_no_live_api_in_ci.py`
- `tests/specialists/enrique/test_enrique_summary_landing.py`
- `tests/specialists/enrique/test_enrique_voice_selection_hil.py`
