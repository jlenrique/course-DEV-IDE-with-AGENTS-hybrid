# Operator Conditional-Gate Addendum Playbook

**Status:** Authored at Slab 3 close. Covers the two open conditional milestones (M2 Wondercraft + M3 Texas) and the pattern for any future conditional milestone (M4 if Slab 4 closes conditional).

**Purpose:** When a Slab close-state is `CLOSED-WITH-CONDITIONAL-M<N>` (per the inheritance pattern established at 2c.4 + 3.6), the operator window is the path to resolving the condition and unblocking the M5 SHIP verdict at 5a.5. This playbook tells you how.

---

## Why conditional milestones exist

The migration's HIL discipline + sandbox-AC governance distinguishes two evidence categories:

- **Behavioral evidence** (architectural/runtime correctness) — verifiable in dev-agent windows via shipped Python deps + pytest.skip on missing service
- **Live-API evidence** (real third-party calls; cost-incurring; operator-discretion) — operator-gated; CANNOT be incurred autonomously by dev agents

When a Slab close has full behavioral pass but a live-API operator-window deferred, it closes `CONDITIONAL-GREEN` per `W-R1-3.6-4` bounded-trigger rule. The condition is the operator-window completion. M5 SHIP verdict at 5a.5 reads all conditional states and either:
- (a) resolves them to GREEN-LIGHT pre-vote (operator addendum landed)
- (b) carries them forward as `SHIP-CONDITIONAL` (with named window for resolution)
- (c) escalates to BLOCK if multiple conditions persist

---

## M2 — Wondercraft live podcast artifact addendum (per Story 2c.2 AC-D-OP)

**Status as of Slab-3 close:** `CONDITIONAL-GREEN-PENDING-OPERATOR-ADDENDUM` per `_bmad-output/implementation-artifacts/slab-2c-m2-acceptance-verdict.md`.

**What's needed:** real podcast artifact produced via live Wondercraft API call against the migrated `wanda` specialist.

**Cost ceiling:** $5.00 for `create_scripted_podcast` (production-quality 8-min explainer); fallback ceiling $1-2 for `create_podcast` (simpler format) per A-R4-2c.2.

### Operator workflow

```bash
# 1. Verify Wondercraft API key present
echo $env:WONDERCRAFT_API_KEY  # PowerShell; should print non-empty

# 2. Run the live test with --run-live opt-in
.venv/Scripts/python.exe -m pytest \
    tests/specialists/wanda/test_wanda_live_api_artifact.py \
    --run-live -v -s

# 3. Inspect emitted artifact
ls tests/fixtures/specialists/wanda/live_artifacts/2026-04-XX/
# Expect: <sha256>.mp3 + LIVE_ARTIFACT_METADATA.md

# 4. Verify metadata round-trip
.venv/Scripts/python.exe -m pytest \
    tests/specialists/wanda/test_wanda_live_artifact_metadata_round_trip.py -v
```

### Paste the addendum

Open `_bmad-output/implementation-artifacts/slab-2c-m2-acceptance-verdict.md`. Append a new section:

```markdown
## Operator-Window Addendum — Story 2c.2 AC-D-OP Live Wondercraft Evidence

**Operator:** <your-id>
**Window opened:** 2026-04-XX
**Window closed:** 2026-04-XX

**Trial-id:** <UUID4 from test run>
**Artifact path:** `tests/fixtures/specialists/wanda/live_artifacts/2026-04-XX/<sha256>.mp3`
**Artifact format:** `scripted` OR `simple-fallback` (per AC-D-OP-FALLBACK enum)
**Cost:** $X.XX (per Wondercraft API response)
**Voice-ID used:** `<voice-id>`
**Script SHA256:** `<sha256>`
**Duration:** XXXs (range-bounded 4*60 ≤ duration ≤ 10*60 per Murat M-R33)
**Sha256 round-trip:** PASS (filesystem sha256 matches LIVE_ARTIFACT_METADATA.md sha256)

**M2 verdict transitions:** CONDITIONAL-GREEN-PENDING-OPERATOR-ADDENDUM → GREEN-LIGHT
```

### Update sprint-status

```bash
# Edit _bmad-output/implementation-artifacts/sprint-status.yaml
# Find the migration-epic-2c-slab-2-wondercraft-pilot row
# Change trailing comment: replace "CONDITIONAL-GREEN-PENDING-OPERATOR-ADDENDUM" with "GREEN-LIGHT 2026-04-XX"
```

### Update deferred-inventory

Mark `2c-3-m2-verdict-conditional-on-2c-2-live-artifact` as `RESOLVED-AT-OPERATOR-WINDOW-<date>` in `_bmad-output/planning-artifacts/deferred-inventory.md`.

### Commit

```bash
git add _bmad-output/implementation-artifacts/slab-2c-m2-acceptance-verdict.md \
        _bmad-output/implementation-artifacts/sprint-status.yaml \
        _bmad-output/planning-artifacts/deferred-inventory.md \
        tests/fixtures/specialists/wanda/live_artifacts/2026-04-XX/
git commit -m "ops(M2): operator-window addendum — live Wondercraft artifact evidence

Story 2c.2 AC-D-OP closed via live API call producing real <format> podcast
artifact at <cost>. M2 verdict transitions CONDITIONAL-GREEN → GREEN-LIGHT.

Resolves 2c-3-m2-verdict-conditional-on-2c-2-live-artifact."
```

---

## M3 — Texas live retrieval evidence addendum (per Story 3.6 AC-D)

**Status as of Slab-3 close:** `CONDITIONAL-GREEN-PENDING-OPERATOR-ADDENDUM` per `_bmad-output/implementation-artifacts/slab-3-m3-acceptance-verdict.md`.

**What's needed:** Texas AC-B-OP live-wire retrieval evidence per 2a.4 deferred-inventory binding (`2a.4-followon-ac-b-op-live-retrieval`) with M1-M5 test discipline per Murat hard-caveat point c.

### Helper script (pre-authored at Story 2a.4)

```bash
.venv/Scripts/python.exe scripts/utilities/ac_b_op_texas_live_retrieval_evidence.py \
    --directive tests/fixtures/specialists/texas/ac_b_op_directive.yaml \
    --bundle-dir <operator-supplied-output-path>
```

**What the script produces:**
- M1: 7 parametrized parse-branch test results against actual scite/Consensus MCP responses
- M2: sha256 baseline verifications (sanctum lock + NFR-I5 retrieval-contract preservation)
- M3: subprocess-dispatch-latency p50/p95 measurements (FR54 substitute metric per 2a.4 close)
- M4: two-sided assertions on parse outcome AND resolution-trail tag
- M5: filled evidence Markdown block ready for paste

### Provider-failure isolation policy (per W-R1-3.6-1)

If one provider (e.g., scite OR Consensus) hard-fails during the live window, the harness is designed to graceful-degrade per-provider PASS/FAIL/SKIP — one flaky provider does NOT fail entire AC-B-OP. Inspect the per-provider report; if ≥1 provider passes M1-M5, evidence is acceptable.

### Paste the addendum

Open `_bmad-output/implementation-artifacts/slab-3-m3-acceptance-verdict.md`. The §"Texas AC-B-OP Live Evidence" section already has DEFERRED-PENDING-OPERATOR-WINDOW placeholders. Replace each with:

```markdown
M1: PASS - 7 parse-branch cases against scite + Consensus MCP responses on <date>; per-provider results at <bundle-dir>/m1-results.json
M2: PASS - sanctum-lock sha256 verified at <hash>; NFR-I5 retrieval-contract sha256 verified at <hash>
M3: PASS - subprocess-dispatch-latency p50=<ms>, p95=<ms> baseline recorded at <bundle-dir>/m3-latency.json
M4: PASS - two-sided assertions on parse outcome + resolution-trail tag verified per <test-output>
M5: PASS - this evidence block pasted by operator on <date>; bundle-dir at <path>
```

### Update sprint-status + deferred-inventory + commit

Same pattern as M2 above. Mark `2a.4-followon-ac-b-op-live-retrieval` as `RESOLVED-AT-OPERATOR-WINDOW-<date>` in deferred-inventory.

```bash
git commit -m "ops(M3): operator-window addendum — Texas live-wire retrieval evidence

Story 3.6 AC-D closed via Texas AC-B-OP helper-script run against live scite +
Consensus MCP responses. M1-M5 evidence pasted to slab-3-m3-acceptance-verdict.md.
M3 verdict transitions CONDITIONAL-GREEN → GREEN-LIGHT.

Resolves 2a.4-followon-ac-b-op-live-retrieval per Murat hard-caveat binding."
```

---

## M4 (if Slab 4 closes conditional) — TBD

If Codex's Slab-4 close at 4.7 surfaces a conditional-M4 state per `W-R1-3.6-4` evidence-completeness gap pattern, this section will be authored during the Slab-4 review to document the specific addendum workflow.

**Anticipated conditional triggers at Slab 4:**
- 4.3 LangSmith trace-link in bmad-code-review finding (FR42 evidence) — may defer to operator-paste at 4.7
- 4.4 ledger Postgres connection unavailable during 4.4 dev — may defer to operator-window
- 4.6 sanctum_watcher live test against running trial — may defer

---

## Pre-M5 conditional-state audit checklist

Before convening the 5a.5 6-agent party-mode for M5 ship verdict, run this audit:

- [ ] M2 verdict state in `slab-2c-m2-acceptance-verdict.md`: GREEN-LIGHT or CONDITIONAL?
- [ ] M3 verdict state in `slab-3-m3-acceptance-verdict.md`: GREEN-LIGHT or CONDITIONAL?
- [ ] M4 verdict state in `slab-4-m4-acceptance-verdict.md` (post-Slab-4 close): GREEN-LIGHT or CONDITIONAL?
- [ ] Each conditional state has either (a) operator-window-resolved-pre-vote OR (b) named window for SHIP-CONDITIONAL carry-forward OR (c) escalation flag for BLOCK
- [ ] `slab-3-m5-dispatch-registry-swap` deferred-inventory entry status — pre-swap OR swapped (M5 verdict path triggers the swap if SHIP)

The party-mode prompt at 5a.5 enumerates each prior M-state explicitly per Decision #2 of `migration-5a-5-m5-ship-decision-and-slab-close.md`. Pre-vote resolution simplifies the prompt; carry-forward conditions are explicitly named in the verdict text.

---

## See also

- [`docs/operator/trial-run-runbook.md`](trial-run-runbook.md) — first-trial step-by-step
- [`docs/operator/post-m5-runbook.md`](post-m5-runbook.md) — post-M5 verdict-path operations
- [`_bmad-output/planning-artifacts/deferred-inventory.md`](../../_bmad-output/planning-artifacts/deferred-inventory.md) — full deferred-work inventory
- Story specs:
  - [`_bmad-output/implementation-artifacts/migration-2c-2-wanda-l5-l6-expertise-and-live-api.md`](../../_bmad-output/implementation-artifacts/migration-2c-2-wanda-l5-l6-expertise-and-live-api.md) — M2 source
  - [`_bmad-output/implementation-artifacts/migration-3-6-e2e-trial-run-and-m3-acceptance-slab-close.md`](../../_bmad-output/implementation-artifacts/migration-3-6-e2e-trial-run-and-m3-acceptance-slab-close.md) — M3 source
