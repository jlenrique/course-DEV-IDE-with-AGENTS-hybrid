# Operator Conditional-Gate Addendum Playbook

**Status:** Actualized 2026-04-26 for M5 `SHIP-CONDITIONAL` window through **2026-05-03**.

**Purpose:** Operator-window addendum templates for the M5 carried conditions. The current state has four open conditions plus one resolved condition retained for provenance:

| Condition | Current state | Closure owner |
|---|---|---|
| M2 Wondercraft live artifact/operator addendum | OPEN | Operator |
| M3 Texas live retrieval operator window | OPEN | Operator |
| Story 5a.2 production clone-launch equivalence | OPEN | Operator after launcher exists |
| `slab-3-m5-dispatch-registry-swap` | RESOLVED 2026-04-26 | Codex, no operator window |
| Plausible-Token Substrate Contamination | REMEDIATED-CODE / PENDING-LIVE-VERIFICATION | Operator live-OpenAI smoke |

---

## Why conditional milestones exist

The migration's HIL discipline + sandbox-AC governance distinguishes two evidence categories:

- **Behavioral evidence** (architectural/runtime correctness) — verifiable in dev-agent windows via shipped Python deps + pytest.skip on missing service
- **Live-API evidence** (real third-party calls; cost-incurring; operator-discretion) — operator-gated; CANNOT be incurred autonomously by dev agents

When a Slab close has full behavioral pass but a live-API operator-window deferred, it closes `CONDITIONAL-GREEN` per `W-R1-3.6-4` bounded-trigger rule. M5 has already carried those states forward as `SHIP-CONDITIONAL`; this playbook is now the paste-template source for closing them cleanly inside the named window.

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

## 5a.2 — Production clone-launch equivalence addendum

**Status:** OPEN until one real production-clone trial is launched through `app.marcus.cli trial start --preset production --input <corpus-path>` against live OpenAI and the cost report is written under `state/config/runs/<trial-id>/`.

### Paste the addendum

Open `_bmad-output/implementation-artifacts/5a-2-parity-verdict.md` and append:

```markdown
## Operator-Window Addendum — Story 5a.2 Production Clone-Launch Equivalence

**Operator:** <your-id>
**Window opened:** 2026-04-XX
**Window closed:** 2026-04-XX

**Trial-id:** `<trial-id>`
**Invocation:** `.venv/Scripts/python.exe -m app.marcus.cli trial start --preset production --input <corpus-path>`
**Corpus path:** `<corpus-path>`
**LangSmith trace:** `<trace-url-or-unavailable-with-reason>`
**Run registry path:** `state/config/runs/<trial-id>/run.json`
**Cost report:** `state/config/runs/<trial-id>/cost-report.md`
**Cascade IDs observed:** `gpt-5`, `gpt-5-mini`, `gpt-5-nano` only
**Result:** PASS

**5a.2 rider transitions:** OPEN production clone-launch equivalence → RESOLVED
```

Then mark `5a-2-production-clone-launcher-and-execution-equivalence-pass` resolved in deferred inventory.

## Plausible-Token Substrate Contamination live-verification addendum

**Status:** REMEDIATED-CODE / PENDING-LIVE-VERIFICATION. Code now references only the real OpenAI catalog snapshot (`gpt-5`, `gpt-5-mini`, `gpt-5-nano`, `gpt-4.1`, `gpt-4.1-mini`, `gpt-4o`, `gpt-4o-mini`, `o3`, `o4-mini`). The condition closes only after the operator runs the live OpenAI cascade-tier smoke with `OPENAI_API_KEY` set.

### Operator workflow

```bash
.venv/Scripts/python.exe -m pytest tests/live/test_openai_cascade_tiers_smoke.py -m live -q
```

### Paste the addendum

Open `_bmad-output/implementation-artifacts/m5-decision.md` and append:

```markdown
## Operator-Window Addendum — Plausible-Token Substrate Contamination Live Verification

**Operator:** <your-id>
**Window opened:** 2026-04-XX
**Window closed:** 2026-04-XX

**Command:** `.venv/Scripts/python.exe -m pytest tests/live/test_openai_cascade_tiers_smoke.py -m live -q`
**Observed live model IDs:** `gpt-5`, `gpt-5-mini`, `gpt-5-nano`
**Result:** PASS — all cascade-tier model IDs resolved at OpenAI and returned non-zero token usage.

**Condition transition:** REMEDIATED-CODE / PENDING-LIVE-VERIFICATION → RESOLVED
```

Then update `_bmad-output/upstream-state.md` by moving the Plausible-Token condition from `Open Conditions` to `Resolved <date>`.

## Dispatch-registry resolved provenance

No operator addendum is required. `slab-3-m5-dispatch-registry-swap` was resolved on 2026-04-26 by promoting both `state/config/dispatch-registry.yaml` and `runtime/graphs/v42/dispatch-registry-snapshot.yaml` to `_status: production` after registered-target import verification.

---

## Conditional-state audit checklist

Before promoting M5 from SHIP-CONDITIONAL to unconditional SHIP, run this audit:

- [ ] M2 verdict state in `slab-2c-m2-acceptance-verdict.md`: GREEN-LIGHT or CONDITIONAL?
- [ ] M3 verdict state in `slab-3-m3-acceptance-verdict.md`: GREEN-LIGHT or CONDITIONAL?
- [ ] 5a.2 production clone-launch equivalence addendum: RESOLVED?
- [ ] Plausible-Token live-OpenAI cascade smoke: RESOLVED?
- [ ] `slab-3-m5-dispatch-registry-swap`: remains RESOLVED and registries remain `_status: production`?

If any open condition remains after 2026-05-03 and the operator has not explicitly extended the window, follow the demotion rule in `docs/operator/post-m5-runbook.md`.

---

## See also

- [`docs/operator/trial-run-runbook.md`](trial-run-runbook.md) — first-trial step-by-step
- [`docs/operator/post-m5-runbook.md`](post-m5-runbook.md) — post-M5 verdict-path operations
- [`_bmad-output/planning-artifacts/deferred-inventory.md`](../../_bmad-output/planning-artifacts/deferred-inventory.md) — full deferred-work inventory
- Story specs:
  - [`_bmad-output/implementation-artifacts/migration-2c-2-wanda-l5-l6-expertise-and-live-api.md`](../../_bmad-output/implementation-artifacts/migration-2c-2-wanda-l5-l6-expertise-and-live-api.md) — M2 source
  - [`_bmad-output/implementation-artifacts/migration-3-6-e2e-trial-run-and-m3-acceptance-slab-close.md`](../../_bmad-output/implementation-artifacts/migration-3-6-e2e-trial-run-and-m3-acceptance-slab-close.md) — M3 source
