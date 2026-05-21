# Migration Story 7b.9: Wanda Port-Shape Onto Scaffold â€” Wondercraft API + Podcast Bed Generation

**Status:** done
**Sprint key:** `migration-7b-9-wanda-port-shape-onto-scaffold`
**Epic:** Slab 7b Specialist Body Activation â€” `epic-slab-7b-specialist-activation-eleven`. **Wave 4** (Class-C; serial after Wave 3 OR parallelizable with Wave-3 tail; Claude-authored spec / Codex dev per NFR-CG17 + D21).
**Pts:** 4 | **Gate:** single (per `docs/dev-guide/migration-story-governance.json::stories.7b-9`; rationale: null; per Slab 2b.1 TEMPLATE pattern) | **K-target:** ~1.4Ã— (target ~33 tests / floor ~25; ~2.9K LOC).
**Author:** **Claude** spec / **Codex** dev. **Review:** **Claude** T11 `bmad-code-review`.
**Wave-4 precondition:** all of Wave 3 (7b.6 + 7b.7 + 7b.8) `done` per epic Story 7b.9 line 845, OR parallel with Wave-3 tail per operator preference. **No conditional gate-mode binding** on 7b.9 itself (no Round-(e) E3 hook).
**Special note:** This story closes the pre-existing `wanda-sanctum-test-expected-files-constant-drift` follow-on (Slab 2c.2 era flake; sanctum file-count drift) via the sanctum-migration-to-6-file-BMB at T2.

---

## Round-(e) Governance Inheritance

Round-(e) freeze landed 2026-04-29. **No load-bearing direct binding** on 7b.9 (single-gate; no k_contract; no conditional_gate_override; no required_ac_reference_paths). E7 unfreeze + version bump + tripwire-events ledger applies generally.

**Class-C two-SKILL.md convention RATIFIED 2026-04-29 (party-mode 4/4 unanimous on option (a); binding for 7b.9):**
- **CREATE NEW persona-skill at `skills/bmad-agent-wanda/SKILL.md`** with minimal FR101 R1-compliant frontmatter + activation hot-load batch referencing `_bmad/memory/bmad-agent-wanda/` BMB sanctum
- **PRESERVE** `skills/bmad-agent-wondercraft/SKILL.md` UNTOUCHED â€” Slab 2b.x era Wondercraft API-mastery skill; consume lazily as API reference
- Mirrors 7b.6 Gary + 7b.7 Kira + 7b.8 Enrique pattern

**T1 readiness verification command:**
```bash
.venv/Scripts/python.exe -c "import json; d = json.load(open('docs/dev-guide/migration-story-governance.json', encoding='utf-8')); assert d['version'] == '2026-04-29-slab7b-twelve-stories'; assert d['stories']['7b-9']['expected_gate_mode'] == 'single-gate'; print('Round-(e) verified PASS for 7b-9')"
```

---

## T1 Readiness Block

### Required-readings cascade (10-reading)

1. **Round-(e) governance JSON** â€” `docs/dev-guide/migration-story-governance.json` Â§`stories.7b-9` (single-gate; expected_pts=4; expected_k_target=1.4; no conditional binding).
2. **Epic + story-level scope** â€” [`epics-slab-7b-specialist-activation-eleven.md`](../planning-artifacts/epics-slab-7b-specialist-activation-eleven.md) Â§Story 7b.9 (lines 838-878).
3. **PRD Â§FR96** â€” Wondercraft API live invocation + podcast/audio bed generation scoped into storyboard's audio track + scaffold-v0.2 alignment (closes pre-Slab-2b client-landed-not-on-scaffold gap).
4. **Sandbox-AC inventory entry `wondercraft` (FR107; Wave 0 LANDED)** â€” [`docs/dev-guide/migration-ac-sandbox-inventory.json`](../../docs/dev-guide/migration-ac-sandbox-inventory.json) Â§`wondercraft`.
5. **7b.6/7b.7/7b.8 Class-C precedents (Wave-3 inheritance)** â€” Gary + Kira + Enrique. Inherit Class-C template (validator), 6-file BMB sanctum at `bmad-agent-{specialist}/`, two-SKILL.md ratified-binding, VCR cassettes, NFR-CG13/19/20, operator-gated AC-N-B canary.
6. **Slab 2b.1 TEMPLATE precedent** â€” [`migration-2b-1-gary-scaffold-migration.md`](migration-2b-1-gary-scaffold-migration.md).
7. **Specialist migration template (R1-R14)** â€” [`docs/dev-guide/specialist-migration-template.md`](../../docs/dev-guide/specialist-migration-template.md).
8. **Pre-existing Wanda sanctum flake** â€” `tests/specialists/wanda/test_wanda_sanctum_populated.py::test_sanctum_digest_nonempty_post_population` fails on `EXPECTED_SANCTUM_FILES` constant drift (5 expected vs 6 actual). Already filed as `wanda-sanctum-test-expected-files-constant-drift` follow-on. **This story closes it naturally** via sanctum-migration to 6-file BMB pattern + parity-test target update.
9. **`scripts/api_clients/wondercraft_client.py`** â€” Wondercraft API client (already shipped; Slab 2c.1 era).
10. **CLAUDE.md** â€” Â§LangChain/LangGraph migration governance + NFR-CG13/19/20 + bmad-memory-gitignore-force-add-policy.

### Wanda current-state probe + drift surfacing

```bash
ls app/specialists/wanda/                              # __init__.py expertise/ graph.py model_config.yaml state.py wondercraft_dispatch.py (Slab 2c.1 era; Wondercraft dispatch present; client-landed BUT NOT on scaffold-v0.2 â€” closes the gap)
ls _bmad/memory/bmad-agent-wanda/                      # PARTIAL: CLONE-FORK-NOTICE.md INDEX.md PERSONA.md access-boundaries.md chronology.md L6-operational/ (5+1 sidecar-style; pre-Slab-7b convention; needs migration to canonical 6-file BMB)
ls _bmad/memory/wanda-sidecar/ 2>/dev/null             # NOT PRESENT (Wanda's sanctum already partially-populated at bmad-agent-wanda/; no separate sidecar dir)
ls skills/bmad-agent-wondercraft/                      # SKILL.md + assets/ + references/ + scripts/ (Slab 2b.x era Wondercraft API-mastery skill; PRESERVED untouched per two-SKILL.md)
ls skills/bmad-agent-wanda/ 2>/dev/null                # NOT PRESENT (this story creates per two-SKILL.md ratification)
ls scripts/api_clients/wondercraft_client.py
```

**Three drifts surface at T1:**

**âš ï¸ Drift #1 â€” Sanctum-migration: 5+1-sidecar pattern â†’ 6-file BMB:** Wanda's existing sanctum at `_bmad/memory/bmad-agent-wanda/` has partial 5-file pattern (CLONE-FORK-NOTICE/INDEX/PERSONA/access-boundaries/chronology) + `L6-operational/` subdir â€” this is older Slab-2c.1 era convention, NOT the Slab 7b canonical 6-file BMB pattern (`INDEX.md` / `PERSONA.md` / `CREED.md` / `BOND.md` / `MEMORY.md` / `CAPABILITIES.md`). **Resolution at T1 (binding):** migrate to 6-file BMB pattern at the same path. Specifically:
- KEEP existing `INDEX.md` + `PERSONA.md` (canonical names; refresh content per BMB checklist)
- KEEP existing `chronology.md` content + REPLACE filename â†’ `MEMORY.md` (semantic match)
- KEEP existing `access-boundaries.md` content + REPLACE filename â†’ `BOND.md` (semantic match â€” operator-specialist boundary contract)
- ADD new `CREED.md` (operating principles; author per BMB checklist)
- ADD new `CAPABILITIES.md` (skill inventory; consume from `skills/bmad-agent-wondercraft/references/` for content)
- DELETE `CLONE-FORK-NOTICE.md` + `L6-operational/` directory (legacy artifacts; not part of canonical 6-file pattern; preserve content elsewhere if needed but the BMB sanctum stays clean)

**This sanctum migration CLOSES the `wanda-sanctum-test-expected-files-constant-drift` follow-on** (the 5-vs-6 expected-files-constant drift). Update `tests/specialists/wanda/test_wanda_sanctum_populated.py::EXPECTED_SANCTUM_FILES` to the canonical 6-file BMB tuple in lockstep at T2.

**âš ï¸ Drift #2 â€” Class-C two-SKILL.md ratified-binding:** Per Round-(f) party-mode 4/4 unanimous on option (a) ratified post-7b.6 close. **Resolution at T1 (binding):**
- **CREATE** `skills/bmad-agent-wanda/SKILL.md` (NEW persona-skill; minimal FR101 R1 frontmatter `name: bmad-agent-wanda` + persona-focused description; body = activation hot-load batch referencing `_bmad/memory/bmad-agent-wanda/` BMB sanctum). Mirrors 7b.6/7/8 pattern.
- **PRESERVE** `skills/bmad-agent-wondercraft/SKILL.md` UNTOUCHED â€” Slab 2b.x era Wondercraft API-mastery skill; consumed lazily as API reference (line in NEW wanda/SKILL.md says "Use `skills/bmad-agent-wondercraft/` only as Wondercraft API reference material; runtime execution via `app/specialists/wanda/`").

**âš ï¸ Drift #3 â€” scaffold-v0.2 alignment gap:** Per epic Story 7b.9 line 841: "closes the pre-Slab-2b client-landed-not-on-scaffold gap." Wanda's existing `app/specialists/wanda/` was developed in Slab 2c.1 BEFORE the 9-node scaffold canonical was finalized; this story aligns the existing scaffold to canonical SCAFFOLD_NODE_IDS at `tests/integration/scaffold_conformance/scaffold_contract.py`. Verify at T1 + refine `graph.py` if drift.

### Wave 0 + 7b.1 substrate + Wave 1/2a/2b/3 sweeps

```bash
# Wave 0 + 7b.1 substrate
ls docs/dev-guide/bmb-sanctum-alignment-checklist.md docs/dev-guide/sanctum-exception-categories.json docs/dev-guide/operator-control-parity-template.md docs/dev-guide/migration-ac-sandbox-inventory.json skills/bmad-agent-cora/SKILL.md
ls tests/parity/_sanctum_parity_base.py tests/composition/_chain_test_base.py scripts/utilities/validate_parity_test_class_conformance.py

# Waves 1+2a+2b+3 closed (8 stories `done` per epic 7b.9 precondition)
.venv/Scripts/python.exe -c "
import yaml
d = yaml.safe_load(open('_bmad-output/implementation-artifacts/sprint-status.yaml', encoding='utf-8'))
done = lambda k: d['development_status'][k].startswith('done')
required = ['migration-7b-1-texas-hardening','migration-7b-2-quinn-r-hardening','migration-7b-3-vera-hardening','migration-7b-4-irene-pass1-refresh','migration-7b-5-tracy-port-shape-sidecar','migration-7b-6-gary-port-shape','migration-7b-7-kira-port-shape','migration-7b-8-enrique-port-shape']
assert all(done(k) for k in required), f'Wave 3 not fully closed: {[k for k in required if not done(k)]}'
print('Wave 1+2a+2b+3 all closed')
"

# FR107 sandbox-AC `wondercraft` entry present
.venv/Scripts/python.exe -c "import json; d = json.load(open('docs/dev-guide/migration-ac-sandbox-inventory.json', encoding='utf-8')); assert 'wondercraft' in d['notes']; print('wondercraft entry present')"

# Class-C template active in validator (from 7b.6 close)
.venv/Scripts/python.exe scripts/utilities/validate_parity_test_class_conformance.py tests/parity/  # PASS expected
```

### Sandbox-AC validator pre-flight

```bash
.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py \
  _bmad-output/implementation-artifacts/migration-7b-9-wanda-port-shape-onto-scaffold.md
```
Expect PASS.

### Standing pre-flight items

1. Severance posture confirmed.
2. `state/config/substrate-frozen-paths.yaml` honored â€” no diff to `app/marcus/orchestrator/dispatch_adapter.py:70-95`.
3. NFR-T9-T12 wall-clock ceilings hold.

---

## Story

As a **migration dev agent**,
I want **Wanda to execute a Class-C port-shape onto canonical scaffold-v0.2 â€” Wondercraft API live invocation via `wondercraft_client.py` + podcast/audio bed generation scoped into the storyboard's audio track + 9-node scaffold conformance verified per `SCAFFOLD_NODE_IDS` (closes the pre-Slab-2b client-landed-not-on-scaffold gap) â€” AND I want Wanda's sanctum migrated from the Slab-2c.1 5+1 sidecar pattern to the canonical 6-file BMB pattern at `_bmad/memory/bmad-agent-wanda/` AND I want the Class-C two-SKILL.md convention applied (NEW persona-skill at `skills/bmad-agent-wanda/SKILL.md` + PRESERVE existing `skills/bmad-agent-wondercraft/SKILL.md`)**,
So that **(a) Trial-2 reaches G2 with real Wanda podcast beds in the storyboard's audio track integrated with Enrique narration, (b) the scaffold-alignment gap closes (Wanda joins the canonical 9-node scaffold conformance suite), (c) the pre-existing `wanda-sanctum-test-expected-files-constant-drift` flake CLOSES naturally via sanctum-migration to canonical 6-file BMB, and (d) SG-4 GREEN for Wanda via Class-C template inheritance**.

---

## Acceptance Criteria

All ACs are dev-agent-executable (sandbox-AC compliant). Live-API verification wraps via `httpx` + `wondercraft_client.py` with `pytest.skip(...)`; live canary deferred to operator-gated AC-9-B Completion-Notes.

### AC-7b.9-A â€” T1 readiness + drift resolution

**Given** the Wave 1+2a+2b+3 closure preconditions + Class-C template active + Round-(e) E7 unfreeze
**When** the dev agent runs T1 readiness
**Then** all 10 readings cascade complete; Round-(e) verification command exits 0; Wave-0 + 7b.1-T2 + Waves 1-3 sweep PASS; sandbox-AC validator PASS pre-flight
**And** Drift #1 resolution recorded: sanctum migration plan from 5+1 sidecar â†’ 6-file BMB at `_bmad/memory/bmad-agent-wanda/`
**And** Drift #2 resolution recorded: two-SKILL.md ratified-binding (CREATE wanda; PRESERVE wondercraft)
**And** Drift #3 acknowledged: scaffold-v0.2 alignment gap closed at T3.

### AC-7b.9-B â€” 9-node scaffold port-shape per Slab 2b.1 TEMPLATE + scaffold-v0.2 alignment

**Given** the canonical 9-node scaffold contract at `tests/integration/scaffold_conformance/scaffold_contract.py::SCAFFOLD_NODE_IDS`
**And** Wanda's existing scaffold at `app/specialists/wanda/graph.py` (Slab 2c.1 era; pre-canonical-9-node-finalized)
**When** the dev-agent (Codex) refines Wanda's port-shape
**Then** `app/specialists/wanda/_act.py` lands with bounded body (â‰¤150 LOC AC-B ceiling) invoking `wondercraft_client.py`
**And** `app/specialists/wanda/graph.py` builds the 9-node scaffold conformant with `SCAFFOLD_NODE_IDS` (closes the pre-Slab-2b client-landed-not-on-scaffold gap per FR96)
**And** `validate_scaffold("wanda", build_wanda_graph()).is_conforming is True`; ruff clean; import-linter C1 lane-isolation PASS.

### AC-7b.9-C â€” Wondercraft API live invocation + podcast/audio bed generation

**Given** the FR96 contract: Wondercraft API live invocation + podcast/audio bed generation scoped into storyboard's audio track
**When** Wanda dispatched at G2 (post-Enrique narration)
**Then** Wanda's `_act` body invokes `WondercraftClient.generate_audio_bed(...)` via thin wrapper around `scripts/api_clients/wondercraft_client.py`
**And** podcast/audio beds land in the storyboard's audio track scope: `[BUNDLE_PATH]/assembly-bundle/audio/beds/<bed_id>.{mp3|wav}`
**And** beds integrate with Enrique's narration (downstream cohesion verified via chain test).
**Test pin:** `tests/specialists/wanda/test_wanda_audio_bed_generation.py` â€” VCR cassette; assert bed-generation invocation shape + audio-track integration.

### AC-7b.9-D â€” Wanda sanctum migration: 5+1 sidecar â†’ canonical 6-file BMB

**Given** Wanda's existing sanctum at `_bmad/memory/bmad-agent-wanda/` (CLONE-FORK-NOTICE.md/INDEX.md/PERSONA.md/access-boundaries.md/chronology.md/L6-operational/)
**And** the Slab 7b canonical 6-file BMB pattern (Texas/Quinn-R/Vera/Gary precedent)
**When** the dev-agent migrates the sanctum
**Then** `_bmad/memory/bmad-agent-wanda/` lands with EXACTLY 6 files (no extras, no subdirs):
  - `INDEX.md` â€” refresh content from existing INDEX.md + Slab 7b BMB conventions
  - `PERSONA.md` â€” refresh content from existing PERSONA.md
  - `CREED.md` â€” NEW (operating principles per BMB checklist)
  - `BOND.md` â€” NEW (operator-specialist boundary contract; consume content from existing access-boundaries.md as starter)
  - `MEMORY.md` â€” NEW (cumulative continuity; consume content from existing chronology.md as starter)
  - `CAPABILITIES.md` â€” NEW (skill inventory; consume from `skills/bmad-agent-wondercraft/references/` for canonical capability descriptions)
**And** `CLONE-FORK-NOTICE.md` + `L6-operational/` REMOVED from sanctum (legacy artifacts; preserve content elsewhere if operator wants but BMB sanctum stays clean per FR101 R1 6-file pattern).
**And** the legacy file content is NOT lost â€” translated/folded into the new 6-file pattern.

### AC-7b.9-E â€” Class-C two-SKILL.md convention (party-mode-ratified binding)

**Given** the Round-(f) party-mode 4/4 unanimous ratification of two-SKILL.md as canonical Class-C
**When** the dev-agent commits Wanda port-shape
**Then** `skills/bmad-agent-wanda/SKILL.md` (NEW) lands with minimal FR101 R1-compliant frontmatter:
  - YAML frontmatter MINIMAL: `name: bmad-agent-wanda` + persona-focused description (e.g., "Wanda generates podcast and audio beds for storyboard audio tracks via Wondercraft API.")
  - Body = activation hot-load batch referencing `_bmad/memory/bmad-agent-wanda/` 6-file BMB (mirrors 7b.6 Gary `skills/bmad-agent-gary/SKILL.md` pattern)
  - Final line documenting "Use `skills/bmad-agent-wondercraft/` only as Wondercraft API reference material; runtime execution via `app/specialists/wanda/`."
**And** `skills/bmad-agent-wondercraft/SKILL.md` is verified UNTOUCHED â€” Slab 2b.x era API-mastery skill; consume lazily as reference; NOT modified by this story.

### AC-7b.9-F â€” `wanda-sanctum-test-expected-files-constant-drift` flake closure

**Given** the pre-existing flake `tests/specialists/wanda/test_wanda_sanctum_populated.py::test_sanctum_digest_nonempty_post_population` fails on `EXPECTED_SANCTUM_FILES` constant drift (5 expected vs 6 actual; flake from Slab 2c.2 era)
**And** the sanctum-migration to canonical 6-file BMB at AC-D
**When** the dev-agent updates the test's `EXPECTED_SANCTUM_FILES` constant
**Then** `EXPECTED_SANCTUM_FILES = ("INDEX.md", "PERSONA.md", "CREED.md", "BOND.md", "MEMORY.md", "CAPABILITIES.md")` in lockstep with sanctum migration
**And** `tests/specialists/wanda/test_wanda_sanctum_populated.py::test_sanctum_digest_nonempty_post_population` PASSES post-migration
**And** deferred-inventory follow-on `wanda-sanctum-test-expected-files-constant-drift` â†’ CLOSED at this story T2.

### AC-7b.9-G â€” SG-4 Sanctum Alignment (FR100 + FR101 â€” Wanda enforcement)

**Given** the SG-4 sanctum-alignment requirement
**When** the dev-agent commits Wanda port-shape
**Then** `skills/bmad-agent-wanda/SKILL.md` (NEW per AC-E) is verified option-a sanctum-aligned per BMB checklist (FR108)
**And** the sanctum dir at `_bmad/memory/bmad-agent-wanda/` carries the canonical 6-file BMB pattern (per AC-D)
**And** the parity test `tests/parity/test_skill_md_sanctum_alignment.py` PASSES for Wanda with Class-C template assertions.

### AC-7b.9-H â€” FR105 per-specialist parity test (Class-C template inheritance)

**Given** the Class-C template active in validator from 7b.6 close
**When** the dev-agent (Codex) authors Wanda's activation-contract test
**Then** `tests/parity/test_wanda_activation_contract.py` (flat) lands inheriting `SanctumParityTestBase` with `class_template_id = "C"`, `specialist_name = "wanda"`
**And** Class-C template assertions PASS (6-file BMB sanctum + Wondercraft API binding via wondercraft_client.py + VCR cassettes + credential register entry + rate-limit budget + cold-activation smoke)
**And** `validate_parity_test_class_conformance.py` PASSES (NO new template extension; Class-C inherited from 7b.6 unchanged).

### AC-7b.9-I â€” Live-API-on-CI strict prohibition (NFR-CG13)

**Given** NFR-CG13 strict prohibition
**When** the dev-agent (Codex) authors tests
**Then** `tests/specialists/wanda/` use VCR cassettes under `tests/fixtures/specialist-replay/wanda/`
**And** `scripts/utilities/detect_live_api_in_tests.py` AST-scan PASSES
**And** dev-agent ACs reference live-API only via shipped `httpx` + `wondercraft_client.py` with `pytest.skip(...)`.

### AC-7b.9-J â€” Cache-hit-rate N/A (Class-C inheritance)

**Given** Wanda is REST-API tool-dispatch (no LLM at the Wanda layer; same as Gary/Kira/Enrique)
**Then** **NO cache-hit-rate harness for Wanda** â€” same rationale as Wave-3 siblings (FR106 doesn't generalize to Class-C).

### AC-7b.9-K â€” Credential-rotation register (NFR-CG19) + rate-limit budget (NFR-CG20)

**Given** NFR-CG19 + NFR-CG20 requirements
**When** the dev-agent commits Wanda port-shape
**Then** `state/config/credential-rotation-register.yaml` carries Wondercraft row (provider/owner/rotation_cadence/last_rotated/next_due/secret_store_reference)
**And** per-specialist rate-limit budget declared in `app/specialists/wanda/config.yaml` (`{rate_limit_per_minute, daily_budget_usd, per_invocation_cap_usd}`).

### AC-7b.9-L â€” Sandbox-AC governance + substrate-as-floor invariant

**Given** sandbox-AC + FR113 + NFR-I13
**When** validator runs
**Then** PASS; **no diff to `dispatch_adapter.py:70-95`**
**And** legacy `wondercraft_dispatch.py` consumed (NOT replaced) per substrate-as-floor.

### AC-7b.9-M â€” Chain test inheriting `ChainTestBase`

**Given** NFR-CG14 + 7b.1 substrate
**When** the dev agent authors the Wanda chain test
**Then** `tests/composition/test_wanda_to_compositor_chain.py` lands inheriting `ChainTestBase` (Wanda's audio beds feed Compositor at G3 â€” fixture-replay until 7b.11 lands)
**And** wall-clock <120s.

### AC-7b.9-N â€” 7a.5 specialist-summary-writer integration

**Given** the 7a.5 conversation-persistence contract
**When** Wanda `_act` completes
**Then** Wanda invokes `summary_writer.emit_summary(specialist_id="wanda", gate_id="G2", payload=<verdict>)` per 7a.5 facade.

### AC-7b.9-O â€” Operator-gated AC-9-B (Completion Notes evidence)

**Given** operator-gated AC-9-B (NFR-T11b T5 live canary)
**When** the operator runs T5 live canary against real Wondercraft API
**Then** â‰¤3 canary invocations; cost â‰¤$0.40 per canary
**And** evidence pasted into Completion Notes verbatim (API endpoint, request payload redacted, 200-OK + audio bed URL, cost).

### AC-7b.9-P â€” Close protocol

**Given** all prior ACs PASS + bmad-code-review PASS-or-PATCH-applied + regression baseline holds (incl. Wanda sanctum flake CLOSED per AC-F)
**When** the story closes
**Then**:
  1. Sprint-status flip `done`
  2. Wave-4-close ledger entry (no upstream tripwire trigger; this is informational)
  3. next-session-start-here.md update: pivot to Wave 5a (7b.10 Dan greenfield) + 5b (7b.11 Compositor pending spec) parallel openings
  4. Deferred-inventory updates: `wanda-sanctum-test-expected-files-constant-drift` CLOSED at T2; `class-c-two-skill-md-convention-ratified` CLOSED cumulatively at this story
  5. Standing-guardrail status: SG-4 GREEN for Wanda; Class-C template inheritance proven 4Ã— (Garyâ†’Kiraâ†’Enriqueâ†’Wanda)
  6. Three-line D12 close stub

---

## Tasks / Subtasks

### T1 â€” T1 readiness + drift resolution
- [x] **T1.1** Round-(e) governance JSON verification
- [x] **T1.2** 10-reading cascade
- [x] **T1.3** Wave-1/2a/2b/3 closed (8 stories `done`)
- [x] **T1.4** Class-C template active verification
- [x] **T1.5** Wanda current-state probe â€” 3 drifts (sanctum migration; two-SKILL.md; scaffold-v0.2 alignment)
- [x] **T1.6** Drift resolution recorded
- [x] **T1.7** Sandbox-AC validator pre-flight

### T2 â€” Wanda sanctum migration to canonical 6-file BMB + flake closure (AC-D + AC-F)
- [x] **T2.1** Author 6 BMB files at `_bmad/memory/bmad-agent-wanda/` (translate from existing 5+1 sidecar; INDEX/PERSONA refresh + new CREED + BOND from access-boundaries + MEMORY from chronology + new CAPABILITIES)
- [x] **T2.2** Remove `CLONE-FORK-NOTICE.md` + `L6-operational/` from sanctum (legacy artifacts; preserve content out-of-band if operator wants)
- [x] **T2.3** Update `tests/specialists/wanda/test_wanda_sanctum_populated.py::EXPECTED_SANCTUM_FILES` constant to canonical 6-file tuple
- [x] **T2.4** Verify `tests/specialists/wanda/test_wanda_sanctum_populated.py::test_sanctum_digest_nonempty_post_population` PASSES post-migration
- [x] **T2.5** Close `wanda-sanctum-test-expected-files-constant-drift` follow-on in deferred-inventory

### T3 â€” Class-C two-SKILL.md convention authoring (AC-E)
- [x] **T3.1** Create `skills/bmad-agent-wanda/SKILL.md` (NEW; minimal FR101 R1 frontmatter + activation hot-load batch + line documenting wondercraft as API-mastery reference)
- [x] **T3.2** Verify `skills/bmad-agent-wondercraft/SKILL.md` UNTOUCHED (consume only)

### T4 â€” Wanda `_act` body Wave-4 hardening + scaffold-v0.2 alignment (AC-B + AC-C)
- [x] **T4.1** Refine `app/specialists/wanda/_act.py` â€” bounded body invoking `wondercraft_client.py`
- [x] **T4.2** Refine `app/specialists/wanda/graph.py` â€” 9-node scaffold conformance per `SCAFFOLD_NODE_IDS` (closes scaffold-v0.2 alignment gap per FR96)
- [x] **T4.3** Wire podcast/audio bed generation scoped into storyboard's audio track (`assembly-bundle/audio/beds/<bed_id>.{mp3|wav}`)
- [x] **T4.4** Wire 7a.5 specialist-summary-writer (AC-N)
- [x] **T4.5** Consume legacy `wondercraft_dispatch.py` as helper (NOT replace)
- [x] **T4.6** **AC-B 150-LOC ceiling discipline**

### T5 â€” VCR cassettes + sandbox-AC discipline (AC-I)
- [x] **T5.1** Author VCR cassettes at `tests/fixtures/specialist-replay/wanda/`
- [x] **T5.2** `tests/specialists/wanda/test_wanda_audio_bed_generation.py` (AC-C)
- [x] **T5.3** `tests/specialists/wanda/test_wanda_no_live_api_in_ci.py` â€” AST-scan PASS

### T6 â€” Parity + chain tests (AC-H + AC-M)
- [x] **T6.1** `tests/parity/test_wanda_activation_contract.py` (flat; Class-C inherited template)
- [x] **T6.2** `tests/specialists/wanda/test_wanda_summary_landing.py` (AC-N)
- [x] **T6.3** `tests/composition/test_wanda_to_compositor_chain.py` (AC-M)
- [x] **T6.4** Wall-clock annotations + validator PASS on Class-C

### T7 â€” Credential register + rate-limit budget (AC-K)
- [x] **T7.1** Wondercraft row in `state/config/credential-rotation-register.yaml`
- [x] **T7.2** Rate-limit budget in `app/specialists/wanda/config.yaml`

### T8 â€” SG-4 sanctum alignment verification (AC-G)
- [x] **T8.1** `tests/parity/test_skill_md_sanctum_alignment.py` PASSES for Wanda

### T9 â€” Substrate-as-floor verification (AC-L)
- [x] **T9.1** `git diff` empty on dispatch_adapter.py:70-95

### T10 â€” Regression baseline + sandbox-AC final
- [x] **T10.1** Full regression battery (target: cumulative + ~33 tests; Wanda flake CLOSES; only Desmond out-of-scope flake remains)
- [x] **T10.2** ruff story-scoped clean
- [x] **T10.3** lint-imports 9/9 KEPT
- [x] **T10.4** Sandbox-AC validator final PASS

### T11 â€” Codex G6 self-review
- [x] **T11.1** G6 self-review at `7b-9-codex-self-review-2026-04-XX.md`
- [x] **T11.2** Status flip `in-progress â†’ review`

### T12 â€” Claude bmad-code-review + close (AC-O + AC-P)
- [ ] **T12.1** `bmad-code-review` at `7b-9-code-review-2026-04-XX.md`
- [ ] **T12.2** Remediation cycle 1 if needed
- [ ] **T12.3** Operator-gated AC-9-B if window opens
- [ ] **T12.4** Wave-4-close ledger entry (informational; no upstream trigger)
- [ ] **T12.5** Sprint-status flip done
- [ ] **T12.6** next-session-start-here.md update: Wave 5 (7b.10 + 7b.11) parallel openings
- [ ] **T12.7** Deferred-inventory updates per AC-P.4
- [ ] **T12.8** SG-4 GREEN for Wanda; Class-C template inheritance proven 4Ã—
- [ ] **T12.9** Three-line D12 close stub
- [ ] **T12.10** Commit + push (force-add gitignored sanctum if applicable)

---

## Dev Notes

### Wanda is the LAST Class-C specialist (4Ã— Class-C inheritance closes here)

7b.6 Gary â†’ 7b.7 Kira â†’ 7b.8 Enrique â†’ 7b.9 Wanda. After Wanda, Class-C template has 4 active activation-contract tests. No new Class-C specialists in subsequent waves.

### Sanctum migration is unique to Wanda

Wanda's existing sanctum at `_bmad/memory/bmad-agent-wanda/` is partially-populated from Slab 2c.1 era (pre-canonical-6-file-BMB). This story's sanctum migration is structurally similar to 7b.2 Quinn-R's sidecarâ†’BMB migration (5-fileâ†’6-file) but with content-translation rather than greenfield (Wanda's existing INDEX/PERSONA content is preserved + augmented).

### Class-C two-SKILL.md ratified-binding inheritance

7b.7 + 7b.8 + 7b.9 all follow the convention party-mode-ratified at 7b.6 close. NEW persona-skills at specialist-name paths; PRESERVED API-mastery skills at API-name paths.

### NFR predicates honored

NFR-T9 / T10 (VCR; â‰¤90s) / T11b (â‰¤3 canaries; â‰¤$0.40) / T12.
NFR-CG12 (sandbox-AC inventory `wondercraft`) / CG13 (NO live-API in CI) / CG14 / CG16 / CG17 (Codex dev) / CG19 (credential register) / CG20 (rate-limit budget).
NFR-I9 + I10 + I12 (Class-C template inherited 4Ã—) + I13.

### Known follow-ons

- **`wanda-sanctum-test-expected-files-constant-drift`** â€” CLOSE at T2.5 (in-story; sanctum-migration resolves)
- **`class-c-two-skill-md-convention-ratified`** â€” CLOSE cumulatively at this story (4Ã— Class-C inheritance proven)
- **`bmad-memory-gitignore-force-add-policy`** â€” recurring; affects Wanda sanctum at commit (existing dir; may already be tracked given pre-existing content â€” verify at commit)
- **`wanda-7b-11-compositor-chain-test-fixture-replay`** â€” open; closes at 7b.11 Compositor close (Wave 5b)

### Anti-pattern catalog citations

- **A6** (silent-fixture-stub fallback) â€” closing for Wanda G2 audio-bed generation
- **A11** (sanctum/sidecar pattern drift) â€” Wanda's 5+1 sidecar pattern migrating to 6-file BMB; harvest as A11 fourth example if novel
- **P1** (substrate-as-floor violation) â€” AC-L binding

---

### Project Structure Notes

- `app/specialists/wanda/` â€” already populated; this story REFINES `_act.py` + `graph.py` (scaffold-v0.2 alignment), KEEPS `wondercraft_dispatch.py` helper
- `_bmad/memory/bmad-agent-wanda/` â€” MIGRATED from 5+1 sidecar to canonical 6-file BMB
- `skills/bmad-agent-wanda/` â€” NEW (persona-skill per two-SKILL.md ratification)
- `skills/bmad-agent-wondercraft/` â€” UNTOUCHED (API-mastery reference; consume only)
- `tests/parity/test_wanda_activation_contract.py` â€” NEW (Class-C inherited template)
- `tests/specialists/wanda/test_*.py` â€” NEW + UPDATED (3 behavioral tests + EXPECTED_SANCTUM_FILES constant fix)
- `tests/composition/test_wanda_to_compositor_chain.py` â€” NEW
- `tests/fixtures/specialist-replay/wanda/` â€” NEW VCR cassettes
- `state/config/credential-rotation-register.yaml` â€” UPDATED (Wondercraft row)
- `app/specialists/wanda/config.yaml` â€” NEW (rate-limit budget)

### Detected conflicts or variances

- **Sanctum 5+1 sidecar (legacy) vs canonical 6-file BMB** â€” resolved via T2 migration
- **scaffold-v0.2 alignment gap** â€” resolved at T4.2 graph.py refinement
- **Two-SKILL.md ratified-binding** â€” resolved per Round-(f) party-mode 4/4 unanimous

---

## References

- **Round-(e) governance JSON**: [`docs/dev-guide/migration-story-governance.json`](../../docs/dev-guide/migration-story-governance.json) Â§`stories.7b-9`
- **Epic + story-level scope**: [`epics-slab-7b-specialist-activation-eleven.md`](../planning-artifacts/epics-slab-7b-specialist-activation-eleven.md) Â§Story 7b.9
- **PRD FR96**: [`prd-slab-7b-specialist-activation-eleven.md`](../planning-artifacts/prd-slab-7b-specialist-activation-eleven.md) Â§FR96
- **Sandbox-AC inventory `wondercraft` (FR107)**: [`docs/dev-guide/migration-ac-sandbox-inventory.json`](../../docs/dev-guide/migration-ac-sandbox-inventory.json) Â§`wondercraft`
- **Wave-3 Class-C precedents**: [`migration-7b-6-gary-port-shape.md`](migration-7b-6-gary-port-shape.md) + [`migration-7b-7-kira-port-shape.md`](migration-7b-7-kira-port-shape.md) + [`migration-7b-8-enrique-port-shape.md`](migration-7b-8-enrique-port-shape.md)
- **Slab 2b.1 TEMPLATE**: [`migration-2b-1-gary-scaffold-migration.md`](migration-2b-1-gary-scaffold-migration.md)
- **Wondercraft API client**: [`scripts/api_clients/wondercraft_client.py`](../../scripts/api_clients/wondercraft_client.py)
- **7b.1 substrate**: [`migration-7b-1-texas-hardening.md`](migration-7b-1-texas-hardening.md)
- **7a.5 conversation-persistence**: [`migration-7a-5-conversation-persistence-specialist-summary-writer.md`](migration-7a-5-conversation-persistence-specialist-summary-writer.md)
- **BMB sanctum alignment checklist (FR108)**: [`docs/dev-guide/bmb-sanctum-alignment-checklist.md`](../../docs/dev-guide/bmb-sanctum-alignment-checklist.md)
- **CLAUDE.md** governance + bmad-memory-gitignore-force-add-policy + class-c-two-skill-md-convention-ratified

---

## Dev Agent Record

### Agent Model Used

Codex (GPT-5)

### Debug Log References

- T1 governance pin PASS: `2026-04-29-slab7b-twelve-stories`, 7b.9 single-gate.
- T1 Wave-3 prerequisite reconciled from operator instruction: 7b.8 marked `done`; 7b.6/7b.7/7b.8 all `done`; `wave_3_first_port_tripwire.fired_verdict == false`.
- T1 baseline drift surfaced: legacy Wanda sanctum existed at `_bmad/memory/wanda-sidecar/`, not `_bmad/memory/bmad-agent-wanda/`; content migrated into canonical BMB and legacy sidecar removed.
- Class-C conformance validator PASS with 9 activation contracts.
- Sandbox-AC validator PASS before and after implementation.

### Completion Notes List

- Migrated Wanda to canonical six-file BMB at `_bmad/memory/bmad-agent-wanda/` with exactly `INDEX.md`, `PERSONA.md`, `CREED.md`, `BOND.md`, `MEMORY.md`, and `CAPABILITIES.md`; legacy `wanda-sidecar/` removed after content fold-in.
- Created `skills/bmad-agent-wanda/SKILL.md` and preserved `skills/bmad-agent-wondercraft/SKILL.md` with no diff.
- Added bounded Wanda `_act.py` for Wondercraft audio-bed generation under `assembly-bundle/audio/beds/`, with graph scaffold aligned to canonical 9-node `SCAFFOLD_NODE_IDS`.
- Closed `wanda-sanctum-test-expected-files-constant-drift`; targeted flake test now passes.
- Added Wanda Class-C parity, audio-bed, no-live-API, summary, and compositor-chain tests plus fixture replay cassette.
- Verification: focused Wanda/parity/composition battery `71 passed, 1 skipped, 1 deselected`; broad regression slice `1325 passed, 21 skipped, 1 deselected`; ruff clean; import-linter 9/9 KEPT; pipeline lockstep PASS; live-API detector PASS.
- Operator-gated AC-9-B live canary was not run by Codex; remains for Claude/operator close notes.

### File List

- `_bmad-output/implementation-artifacts/7b-9-codex-self-review-2026-04-29.md`
- `_bmad-output/implementation-artifacts/migration-7b-9-wanda-port-shape-onto-scaffold.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `_bmad-output/planning-artifacts/deferred-inventory.md`
- `_bmad/memory/bmad-agent-wanda/INDEX.md`
- `_bmad/memory/bmad-agent-wanda/PERSONA.md`
- `_bmad/memory/bmad-agent-wanda/CREED.md`
- `_bmad/memory/bmad-agent-wanda/BOND.md`
- `_bmad/memory/bmad-agent-wanda/MEMORY.md`
- `_bmad/memory/bmad-agent-wanda/CAPABILITIES.md`
- `_bmad/memory/wanda-sidecar/` (removed)
- `app/specialists/wanda/_act.py`
- `app/specialists/wanda/config.yaml`
- `app/specialists/wanda/graph.py`
- `app/specialists/wanda/model_config.yaml`
- `app/specialists/wanda/wondercraft_dispatch.py`
- `scripts/utilities/detect_live_api_in_tests.py`
- `skills/bmad-agent-wanda/SKILL.md`
- `state/config/credential-rotation-register.yaml`
- `tests/composition/test_wanda_to_compositor_chain.py`
- `tests/fixtures/composition/wanda-to-compositor/expected-output.yaml`
- `tests/fixtures/specialist-replay/wanda/wondercraft_audio_bed_happy_path.yaml`
- `tests/parity/test_skill_md_sanctum_alignment.py`
- `tests/parity/test_wanda_activation_contract.py`
- `tests/specialists/wanda/test_wanda_act_node_dispatch.py`
- `tests/specialists/wanda/test_wanda_audio_bed_generation.py`
- `tests/specialists/wanda/test_wanda_dispatch_wrapper.py`
- `tests/specialists/wanda/test_wanda_l6_operational_context.py`
- `tests/specialists/wanda/test_wanda_live_api_artifact.py`
- `tests/specialists/wanda/test_wanda_no_live_api_in_ci.py`
- `tests/specialists/wanda/test_wanda_sanctum_populated.py`
- `tests/specialists/wanda/test_wanda_summary_landing.py`

### Change Log

- 2026-04-29: Codex implemented Story 7b.9 T1-T11 and moved status to `review`.
