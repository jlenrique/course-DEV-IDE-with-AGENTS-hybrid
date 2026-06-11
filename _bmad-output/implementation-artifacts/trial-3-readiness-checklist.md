# Trial-3 Readiness Checklist (Operator-Facing)

**Purpose:** end-to-end execution playbook for Trial-3 — the first real production trial against the post-Slab-7c substrate. Trial-3 is the strategic payoff event that validates the orchestrational tail (§01→§15) end-to-end and unblocks Epic 15 (Learning & Compound Intelligence) reactivation.

**Status:** **substrate FULLY HARMONIZED** as of 2026-05-22 (Slab 7c dev-stories closed 2026-05-07 at 36/36; **Epic 34 §02A Downstream-Consumer Coherence FULLY COMPLETE 2026-05-22** at 7/7 stories; commit range `bc477ed..1b59487`). Substrate now carries: §02A composer emitting `ref_id` natively (renamed from `src_id`); Texas wrangler accepting 7-role union + closed `excluded_reason` enum + cross-field invariants + `sme_refs[]` metadata; no temporary translator scaffold; no legacy `directive_composer.py`; integration-boundary green test installed at `tests/integration/test_section_02a_to_wrangler_subprocess_roundtrip.py` (sha256-pinned forensic-anchor `351a57f...` from Trial-3 attempt-2 forensic evidence). Trial-3 attempt-2 launch-failure root cause (untested integration boundary; §02A vs wrangler schema fork) is now closed via the integration-ratchet-first Quinn-synthesis Option 5 pattern.

**Authored:** 2026-05-06 — Claude (post-7c.21 close).
**Substrate-state refresh:** 2026-05-22 — Claude (post-Epic-34 close). Trial-3 execution playbook (§§1-N below) remains authoritative; substrate is now MORE harmonized than the 2026-05-06 baseline (no translator, no legacy composer, integration boundary green-tested + extended through 4 stories + ratified through Epic close).

**Owner of execution:** Operator (with Marcus orchestration). Codex is NOT in scope for Trial-3 dispatch — this is a real-content production run, not a dev-story cycle.

---

## 1. What Trial-3 IS

Trial-3 is a **real production trial** of the LangChain/LangGraph migrated platform end-to-end (§01 Activation through §15 Final Operator Handoff) against a real corpus. It validates:

- All 11 specialists (Texas / Quinn-R / Vera / Irene-Pass1 / Tracy / Gary / Kira / Wanda / Enrique / Dan / Compositor) execute with real content (NOT fixture stubs).
- All 14+ HIL surfaces (per Slab-7c §section packages) accept operator input + emit OperatorVerdict.
- All 5 Marcus-bound writers (gary-slide-content + gary-fidelity-slides + gary-diagram-cards + gary-theme-resolution + gary-outbound-envelope) emit per-plan-unit packages.
- The §15 G5 final-handoff bundle (`section-15-bundle` writer) emits assembly-bundle + DESCRIPT-ASSEMBLY-GUIDE.md regen + Trial3Transcript anchor + slab-close evidence pointer.
- TW-7c-1..6 tripwires remain `not_fired` under real-content execution.
- Cache-hit-rate stays ≥60% (per FR54 measurement substrate; Irene Pass-2 baseline 95.33% from Slab-2a).

**Trial-3 is NOT:**
- A dev-agent task (Codex doesn't run trials; the operator does).
- A unit-test or integration-test run (it's a real LangGraph runtime execution against a real corpus).
- A retrospective ceremony (`bmad-retrospective` is separate; runs after Trial-3 completes).

---

## 2. What's READY (substrate verification per 7c.21 close)

Per the 7c.21 retrospective evidence pack (Section 5 Trial-3 Readiness Verdict; PASS for development closeout):

### 2.1 Tripwire ledger queryability ✅

All TW-7c-1..6 IDs queryable at `_bmad-output/implementation-artifacts/sprint-status.yaml::tripwire_events`:
- TW-7c-1 (gap-rate detection) — concrete row from 7c.20c LAST-CLOSER aggregation; `fired_verdict: not_fired`
- TW-7c-6 (parity flake; 50-run zero-flake baseline) — concrete row from 7c.21 closeout; `fired_verdict: not_fired`
- TW-7c-2..5 — seeded reservation entries; queryable for runtime tripwire firings during Trial-3.

`app.audit.chain.verify_audit_chain` confirms append-only + monotonic-timestamp + parent-trace invariants.

### 2.2 R7a precondition fixtures ✅

Trial-3 R7a fixtures present at:
- `state/config/runs/db276994-edf4-47a2-83bc-771cc214c3c1/` (Trial-2 run-id directory; reference shape)
- `_bmad-output/implementation-artifacts/trial-2-postmortem-2026-05-04.md` (lessons learned)
- `_bmad-output/implementation-artifacts/migration-7c-3a-section-02a-llm-directive-composer-body.md` (composer body reference)

### 2.3 R7b 120/180-min forensic-evidence harness operational ✅

Cache-hit-rate + 5-API smoke harnesses operational in fail-closed skeleton mode:
- `scripts/utilities/run_cache_hit_harness.py --all-specialists`
- `scripts/utilities/run_5_api_smoke.py`

(Note: 7c.21a is currently authoring **live-dispatch** for these harnesses to consume the post-Slab-7c substrate. Trial-3 should dispatch AFTER 7c.21a closes — at that point the harnesses produce authoritative evidence rather than fail-closed skeletons.)

### 2.4 11-HIL class-conformance markers ✅

All 11 specialist activation contracts emit class-conformance markers; validator at `scripts/utilities/validate_parity_test_class_conformance.py` reports PASS at 19 (= 11 activation + 8 decision-card shape-pin).

### 2.5 Trial3Transcript schema landed ✅

`app/models/trial3_transcript.py` (97 LOC) with:
- Closed-enum `GateId = Literal["G1", "G2C", "G3", "G4"]` (pinned to `production_gate_ids(state/config/pipeline-manifest.yaml)` via shape-pin test)
- Closed-enum `TrialEventType = Literal["edit", "approve", "reject", "complete"]`
- Schema hash: `818b740594a7fe95c62a5c8d27399ea6e8a0b77336c2900bdbb5f7cc0ab24491`

Trial-3 events captured by the runtime are validated against this schema.

---

## 3. Prerequisites (verify before launch)

Operator confirms these on the dispatch session:

- [ ] **Slab 7c at 36/36 dev-stories DONE** in `sprint-status.yaml` (7c.21 + 7c.21a both `done`).
- [ ] **Operator-driven Gate-2 of 7c.21 complete** (`bmad-retrospective` triggered + mapping-checklist row-flips party-mode-ratified per FR-7c-42 + per-tripwire firing-rate review per FR-7c-41). Recommended but not strictly blocking.
- [ ] **Real corpus selected** (e.g., Tejal APC C1-M1 corpus from Trial-2 OR a fresh corpus). Path documented.
- [ ] **API credentials in `.env`**: GAMMA_API_KEY + ELEVENLABS_API_KEY + CANVAS_ACCESS_TOKEN + (optional) PANOPTO_CLIENT_ID/SECRET + (optional) WONDERCRAFT_API_KEY + (optional) KLING_ACCESS_KEY/SECRET_KEY + OPENAI_API_KEY (for LLM specialists). Per-cred validation: `node scripts/heartbeat_check.mjs` (it is a Node script, not Python; var names corrected 2026-06-10 scrub).
- [ ] **`PYTHONIOENCODING=utf-8`** set in PowerShell environment per A11 Windows-portability anti-pattern. Verify: `$env:PYTHONIOENCODING == "utf-8"`.
- [ ] **Postgres running natively** (per CLAUDE.md memory `project_no_docker.md`; LangGraph checkpointer relies on local Postgres).
- [ ] **No active git-uncommitted state** that could mask Trial-3 evidence.

---

## 4. Launch sequence

Trial-3 is launched via Marcus orchestrator's CLI surface. The exact command shape depends on the post-7c.21a substrate (live-dispatch wiring); below is the expected pattern based on Slab 6.1 Marcus production-runner contract.

### 4.1 Pre-flight (runtime substrate health)

```powershell
# From repo root (corrected 2026-06-10 scrub: module lives under scripts.utilities)
.venv/Scripts/python.exe -m scripts.utilities.app_session_readiness
```

Confirm: SQLite + Postgres up, all 11 specialists discoverable, all API clients reachable.

### 4.2 Trial-3 dispatch

```powershell
# Marcus CLI launch (exact flag-set TBD per 7c.21a substrate)
.venv/Scripts/python.exe -m app.marcus.cli trial start `
    --preset production `
    --input <path-to-real-corpus-dir> `
    --trial-id trial-3-<date>-<descriptor> `
    --transcript-output _bmad-output/implementation-artifacts/trial-3-transcript-<date>.json
```

The trial advances through §01→§15 (or pauses at first HIL gate awaiting operator input). Per `bmad-session-protocol-session-START.md` and Marcus's HIL discipline: every gate is operator-confirmed; no silent auto-approve.

### 4.3 Per-gate operator interaction

At each HIL gate (§02A → §11 → §15 etc.), Marcus presents the DecisionCard / OperatorVerdict surface. Operator chooses verb:
- `approve` (proceed)
- `edit` (modify content + re-submit)
- `reject` (halt; investigate)
- (At §15 G5) `complete` (fire Marcus §15 bundle emission)

Operator captures evidence inline: cost report, gate timestamps, observed flake/error events.

### 4.4 Tripwire firings during Trial-3

If ANY of TW-7c-1..6 fires during Trial-3:
- **TW-7c-1** (gap-rate): NOT EXPECTED at runtime (it's an AUDIT-AC tripwire; AUDIT-ACs already ran clean at 7c.20a/b/c).
- **TW-7c-2** (Trial-2 forensic-fixture regression): if fires, the 7c.3a §02A composer body has regressed; HALT and investigate.
- **TW-7c-3** (Composition Spec lockstep break): if fires, four-file-lockstep has drifted; HALT.
- **TW-7c-4** (live-dispatch scope-creep): owned by 7c.21a; should not fire post-7c.21a close.
- **TW-7c-5** (UTF-8 violations): code-emit lint; runtime-irrelevant.
- **TW-7c-6** (parity flake; 50-run baseline): AUDIT-style; runtime-irrelevant unless Trial-3 itself triggers the parity suite.

Per AMEND-7d-iii: STOP-on-TW-7c-6-fire; party-mode mitigation. Other tripwires: investigate per parent-story-owner protocol.

---

## 5. Trial3Transcript artifact capture

Per AC-7c.21-A, the trial run emits a `Trial3Transcript` JSON at `--transcript-output` path. Schema:

```json
{
  "trial_id": "<UUID4>",
  "started_at": "<tz-aware ISO8601>",
  "completed_at": "<tz-aware ISO8601 OR null if paused>",
  "events": [
    {
      "event_id": "<UUID4>",
      "gate_id": "G1|G2C|G3|G4",
      "event_type": "edit|approve|reject|complete",
      "event_at": "<tz-aware ISO8601>",
      "operator_id": "<non-empty>",
      "payload_digest": "<sha256-hex>"
    },
    ...
  ],
  "schema_version": 1
}
```

Validate post-trial:
```powershell
.venv/Scripts/python.exe -c "from pathlib import Path; from app.models.trial3_transcript import Trial3Transcript; import json; data = json.loads(Path('<transcript-path>').read_text(encoding='utf-8')); transcript = Trial3Transcript.model_validate(data); print(f'{len(transcript.events)} events captured; trial {transcript.trial_id}')"
```

Anchor (sha256) of the transcript file lands in `Section15Bundle.trial_3_transcript_anchor` if Marcus §15 bundle emission fired (i.e., operator chose `verb=complete` at §15 G5).

---

## 6. Success criteria (Trial-3 PASS)

Trial-3 is PASS when:

- [ ] Reaches §15 G5 with operator verb=`complete` (NOT paused/halted/rejected).
- [ ] All 11 specialists produce real content (zero fixture-stub fallbacks).
- [ ] All 14+ HIL surfaces accept operator input + emit valid OperatorVerdict (verbs match per-surface contracts).
- [ ] All 5 Marcus-bound pre-Gary writers emit per-plan-unit packages.
- [ ] §15 G5 Marcus bundle writer (`section-15-bundle`) emits assembly-bundle + DESCRIPT-ASSEMBLY-GUIDE.md + Trial-3 transcript anchor + slab-close evidence pointer.
- [ ] Cache-hit-rate ≥60% (per FR54).
- [ ] No tripwire fires (TW-7c-1..6 all stay `not_fired`).
- [ ] Trial3Transcript validates against schema; events list non-empty.

**Partial-PASS signals** (operator decides whether to retry or accept):
- Reached G3 cleanly but paused at §11 voice-selection (acceptable for first trial; document why)
- One specialist returns minimal content (e.g., placeholder narration on a slide where source is sparse)
- Single tripwire fire that's clearly unrelated to substrate integrity (operator-judgment call)

**FAIL signals** (HALT; investigate):
- Any specialist returns fixture-stub fallback (substrate not actually engaged)
- Any silent gate-bypass (HIL surface skipped without verdict)
- Schema validation error on Trial3Transcript
- TW-7c-6 fires (parity flake; per AMEND-7d-iii STOP)
- Cache-hit-rate <60% (FR54 floor breach)

---

## 7. Closeout actions

After Trial-3 completes (PASS or FAIL):

1. **Capture transcript artifact** at `_bmad-output/implementation-artifacts/trial-3-transcript-<date>.json`.
2. **Update `migration-master-status`** in `sprint-status.yaml` from `shipped` → `shipped-with-trial-3-evidence`.
3. **File trial postmortem** at `_bmad-output/implementation-artifacts/trial-3-postmortem-<date>.md` (if FAIL; lessons-learned + reactivation triggers for any deferred fixes).
4. **Trigger Slab 7c retrospective** (`migration-epic-slab-7c-orchestrational-tail-retrospective: optional`) if not yet done — Trial-3 evidence informs the retrospective.
5. **Reactivate Epic 15** (Learning & Compound Intelligence) — its hard dependency was "at least one tracked trial run completed"; Trial-3 PASS unblocks 15-1-lite-marcus + the full chain (15-1..15-7).
6. **Schedule next-Trial cadence** (Trial-4 / Trial-5 with different corpora) — Epic 15 needs multiple tracked runs to populate its learning ledger meaningfully.

---

## 8. Rollback / abort path

If Trial-3 FAILs and the failure is clearly a substrate regression (NOT operator error or external API failure):

1. **HALT** the trial; preserve the partial transcript artifact for forensic analysis.
2. **Capture `_artifacts/<trial_id>/`** state directory + `state/runtime/coordination.db` snapshot for replay debugging.
3. **File a Slab 7c regression follow-on** in deferred-inventory.md; describe the substrate gap.
4. **Decide reactivation scope**: targeted fix (single-story bmad-dev-story) vs broader scope (party-mode-debated PRD authoring for Slab 4 reactivation or successor slab).

If failure is operator-error / external-API / corpus-quality (NOT substrate): re-launch with adjusted inputs.

---

## 9. Critical-path AFTER Trial-3 PASS

Per the migration-completion roadmap:

1. **Slab 7c retrospective close** (operator + party-mode; consumes 7c.21 evidence pack + Trial-3 evidence)
2. **Epic 15 reactivation** (Learning & Compound Intelligence; 7 stories: 15-1..15-7)
3. **Epic 16 / 17 / 18 / Post-M5 Greenfield Specialists** (operator-priority-driven)
4. **Slab 7c housekeeping batch** (4 stories: 7c-housekeeping-1 through 7c-housekeeping-4) — can run in parallel with Epic 15 reactivation; cleans up cross-Wave deferred follow-ons

The replatforming brownfield work is **functionally complete after Trial-3 PASS**. Subsequent work is product-iteration on a shipped platform.

---

## 10. References

- `_bmad-output/implementation-artifacts/slab-7c-retrospective-evidence-pack.md` (substrate readiness summary; Section 5 = Trial-3 readiness verdict)
- `_bmad-output/implementation-artifacts/migration-7c-21-integration-parity-suite-slab-7c-closeout.md` (7c.21 spec; AC-C verifies Trial-3 readiness predicates)
- `_bmad-output/implementation-artifacts/migration-7c-21a-epic-3-retirement-live-dispatch-wiring.md` (7c.21a; live-dispatch authoring for Trial-3 harnesses)
- `_bmad-output/implementation-artifacts/trial-2-postmortem-2026-05-04.md` (Trial-2 lessons; failure modes to avoid in Trial-3)
- `app/models/trial3_transcript.py` (transcript schema)
- `_bmad-output/planning-artifacts/prd-slab-7c-orchestrational-tail.md` NFR-7c-R7a + NFR-7c-R7b (readiness preconditions)
- `_bmad-output/planning-artifacts/architecture-langchain-langgraph-migration.md §Decision D12` (cross-slab governance)
- `_bmad-output/planning-artifacts/deferred-inventory.md` (Epic 15 reactivation trigger)
- `bmad-session-protocol-session-START.md` (operator session ramp-up)
- `CLAUDE.md` (project-level governance)
