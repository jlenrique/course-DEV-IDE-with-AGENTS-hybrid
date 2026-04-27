# Operator Trial-Run Runbook

**Status:** Actualized 2026-04-27 for the bounded-MVP ship state. The runtime trial launcher is `python -m app.marcus.cli trial start`; Marcus ad-hoc mode and the migrated-runtime HUD are now documented operator surfaces.

**Purpose:** Step-by-step guide to running a trial against the migrated runtime — Marcus the LangGraph orchestrator (`app/marcus/`) + 14 specialists (`app/specialists/<name>/graph.py`) + HIL DecisionCard gates. Assumes you've completed the README's quick-start (venv + deps + `.env`).

## Mental model — what runs where

The shipped application is **Python + LangGraph**. Marcus the orchestrator is a Python module at `app/marcus/`; specialists are LangGraph nodes; LLM calls go to OpenAI directly via the cascade in `runtime/config/model_cascade.yaml`. **Claude Code is not in the runtime path.** Production trials are pure Python invocation.

Be aware of two distinct "Marcuses":
- **Marcus the runtime** — the Python service. You invoke it from a terminal (CLI), via HTTP, or via MCP. It runs, calls OpenAI, writes artifacts to disk, uploads traces to LangSmith. No Claude involvement.
- **Marcus the BMAD development persona** — a roleplay used in Claude Code sessions for *development* work (planning, scoping, code review, dispatching agent batches). Same archetypal voice, entirely separate mechanism. Useful as a debugging companion *while* the runtime executes elsewhere; not part of the runtime itself.

This runbook covers the runtime. If you want to chat with the BMAD persona to learn or explore, open Claude Code in the repo and say "Marcus, I want to explore." That is development assistance, not runtime execution.

---

## Step 0 — Run ready-for-trial harness

```bash
# Windows
scripts/setup/ready_for_trial.ps1

# macOS/Linux
bash scripts/setup/ready_for_trial.sh
```

The harness runs the preflight sweep, dashboard, M5 audit, cascade validation, model-ID lint guard, catalog-membership test, cascade loading test, ruff, import-linter, and migration pytest slice. Run the raw preflight only for diagnosis:

```bash
.venv/Scripts/python.exe scripts/utilities/trial_run_preflight.py --trial-corpus <path-to-your-corpus>
```

**Possible outcomes:**

| Exit code | What it means | Action |
|---|---|---|
| `0` | All checks pass (warnings allowed) | Proceed to Step 1 |
| `1` | Non-required failures (some features unavailable) | Read the WARN/FAIL detail; decide if degraded-mode is acceptable for your trial |
| `2` | Blocking failures (env vars missing, manifests broken, etc.) | Resolve the FAIL items before proceeding |

**Common WARN states (acceptable for first trial):**
- `migration_state` shows M2 / M3 conditional — operator-window addenda pending; conditional gates do NOT block trial execution, only unconditional-SHIP promotion
- `trial_corpus` not provided — you can run preflight without a corpus to inspect substrate state; provide the corpus at Step 1

---

## Step 1 — Choose your transport

Marcus accepts operator verdicts via THREE transport surfaces (all routed through the same `resume_from_verdict` path per FR34 architectural enforcement; no transport bypasses tamper-evidence):

| Transport | When to use | Invocation |
|---|---|---|
| **CLI** (`app.marcus.cli`) | First-trial; quick experiments; scriptable batch verdicts | `.venv/Scripts/python.exe -m app.marcus.cli trial start --preset production --input <corpus-path> --operator-id <your-id>` |
| **MCP** (`gate.decide`) | Interactive IDE-integrated workflows (Claude Code / Cursor); per-gate manual verdict | Configure your MCP client to point at `app.mcp_server.tools.gate_decide`; then invoke `gate.decide` per gate fire |
| **FastAPI** (`POST /gate/verdict`) | Web UI / external operator surfaces; remote verdict submission | Start the HTTP server (`uvicorn app.http.gate_endpoint:app`); POST OperatorVerdict JSON with `X-Operator-Id` header |

**Recommendation for first trial:** CLI. Fewer moving parts; verdict prompts surface inline in your terminal; subprocess-isolated from any IDE state.

---

## Step 2 — Identify your trial corpus

The trial corpus is the **input content bundle** Marcus orchestrates against. For migration parity testing (Slab 5a.2), this MUST be the same input the primary repo's reference trial used (e.g., `C1-M1-PRES-20260419B`); for first-trial-experimentation, any well-formed input bundle works.

**Corpus shape expectations:**
- Markdown source files for the course content
- YAML/JSON configuration (style guide, voice profile, audience parameters)
- Optional: Reference-set assets (images, prior podcast episodes for voice continuity)

**Path conventions:** corpus typically lives under `course-content/` (per `docs/agent-environment.md`). For trial-run experiments, you may store under `tests/fixtures/trials/<trial-id>/`.

---

## Step 3 — Start the trial

```bash
.venv/Scripts/python.exe -m app.marcus.cli trial start \
    --preset production \
    --input <corpus-path> \
    --operator-id <your-id>
```

**Preset choice:**
- `--preset production` (default) → Plan-and-Execute supervisor reasoning loop (FR27); manifest-driven specialist routing
- `--preset explore` → ReAct supervisor reasoning loop (operator-driven exploration of alternative paths)

**Model catalog:** the production cascade uses real OpenAI catalog IDs only: `gpt-5`, `gpt-5-mini`, and `gpt-5-nano` for the current cascade tiers. Do not substitute historical fictitious IDs.

**What happens at start:**
1. Marcus's `get_facade()` instantiates fresh per FR30 cold-read sanctum (no in-memory continuity from prior sessions)
2. Sanctum digest computed + recorded as `marcus_fingerprint = (sha256, session_id)` in RunState
3. Trial-id assigned (UUID4); checkpoint thread namespace set to `run/{trial_id}` (distinct from Cora's `dev/{story_id}` per FR40)
4. Pipeline-manifest §-IDs (e.g., 01, 02, 02A, ..., 15) executed in declared order
5. At each gate (G1, G2C, G3, G4), Marcus emits a DecisionCard + `interrupt()` checkpoint pauses the run pending operator verdict

---

## Step 4 — Inspect each DecisionCard at gate fire

When the trial pauses at a gate, Marcus emits a `DecisionCard` to your operator transport. Each card carries:

| Field | What it tells you |
|---|---|
| `card_id` / `trial_id` / `gate_id` | Identity |
| `drafted_proposal` | What Marcus proposes (the artifact under review at this gate) |
| `evidence` | What evidence Marcus collected supporting the proposal |
| `risks` | What Marcus flagged as risks (operator should weight in verdict decision) |
| `verb` | The proposed verb Marcus suggests (`approve` / `edit` / `reject`); operator may override |
| `meta.cache_state` | `healthy` (all nodes on default cascade) / `mixed` (active overrides) / `cold` (cache prefix invalidated) |
| `meta.affected_nodes` | Downstream nodes impacted by your decision |
| `meta.override_trail` | Prior overrides applied this trial |
| `meta.reject_rate` | Historical reject-rate for this gate (KPI tracking) |
| `meta.party_mode_contributions` | If party-mode-as-interrupt fired, the multi-persona contributions feeding this card |
| `meta.sanctum_warnings` | If sanctum mutation detected during this trial, the cited file + suggested invalidating commit |

---

## Step 5 — Issue a verdict

Three verbs available:

### `approve`

```bash
.venv/Scripts/python.exe -m app.marcus.cli gate decide \
    --trial-id <id> --gate-id G2C \
    --verb approve \
    --decision-card-digest <digest-from-card> \
    --operator-id <your-id>
```

Resumes the trial; downstream nodes consume the proposal as-is.

### `edit`

```bash
.venv/Scripts/python.exe -m app.marcus.cli gate decide \
    --trial-id <id> --gate-id G2C \
    --verb edit \
    --edit-payload <path-to-edit.json> \
    --decision-card-digest <digest-from-card> \
    --operator-id <your-id>
```

`edit_payload` (JSON file path) MUST be present iff verb is `edit` (cross-field validator enforces). The edit propagates downstream via `RunState`.

### `reject`

```bash
.venv/Scripts/python.exe -m app.marcus.cli gate decide \
    --trial-id <id> --gate-id G2C \
    --verb reject \
    --decision-card-digest <digest-from-card> \
    --operator-id <your-id>
```

Rejects the proposal; reject-rate KPI updates. Downstream behavior depends on per-gate semantics (some gates re-loop to re-draft; others terminate the trial).

**Tamper-evidence enforcement (FR34):** the `decision-card-digest` MUST match the digest emitted by Marcus on the card you're verdict-ing. Any mismatch raises `GateError("digest_mismatch")` and refuses to resume — protects against verdict-replay across trials. Cross-trial replay also blocked by anti-replay binding tuple `(card_content + trial_run_id + issuance_timestamp + server_nonce)` per Story 3.3 W-R1-3.3-2.

---

## Step 6 — Optional: model overrides mid-trial

If you want to override a specialist's model mid-trial (FR24):

```bash
# Phase 1 — submit_override returns an OverrideWarning (NO state mutation yet)
.venv/Scripts/python.exe -m app.marcus.cli gate override-submit \
    --trial-id <id> --node-id <node> --new-model <model-name>
```

Marcus computes `compute_cache_impact` and returns:
- `estimated_cost_delta_usd` — projected cost impact
- `affected_nodes` — downstream nodes whose cache state changes
- `cache_state_delta` — before/after cache_state enum transitions
- `confirm_token` — sha256 binding the impact summary you saw

```bash
# Phase 2 — apply_override consumes the confirm_token
.venv/Scripts/python.exe -m app.marcus.cli gate override-apply \
    --trial-id <id> --confirm-token <token-from-phase-1>
```

Confirm-token expires 5 min after issuance; stale tokens raise `OverrideTokenStaleError`. Subsequent DecisionCards reflect `meta.cache_state = "mixed"` until trial close.

---

## Step 7 — Trial close

At final gate (G4) verdict, Marcus's `finalize` + `handoff` nodes:
- Emit final `LedgerEvent kind="verdict"` per Slab 4.4
- Compute reject-rate KPI update
- Capture trial artifacts to disk
- Mark trial `closed_at` in checkpointer storage
- Optionally: capture Marcus envelope for baseline regression-detection (per Story 3.6 W-R7-3.1 baseline pattern; first-trial captures NEW baseline)

**Post-close inspection:**
- LangSmith trace: `https://smith.langchain.com/traces/<trace_id>` (one trace per trial; spans per node)
- Ledger query: `SELECT * FROM ledger_events WHERE trial_id = '<id>'` (verdict events + override events + sanctum_mutations)
- Trial artifacts: depends on pipeline (typically under `course-content/staging/<trial-id>/` or similar)

---

## Step 8 — Replay verification (optional; recommended for parity trials)

```bash
.venv/Scripts/python.exe -m app.replay.regression --trial-id <id> --mode warn-on-clone
```

Replays the trial from final checkpoint; verifies pack-hash + sanctum-fingerprint + Marcus-envelope baseline; reports drift if any.

**Mode choice:**
- `--mode fail-loud` (CI default) — drift raises ReplayError + non-zero exit
- `--mode warn-on-clone` (operator default) — drift continues with snapshot fallback + provenance log per architecture D1

---

## Common surprises during your first trial

| Surprise | Cause | Resolution |
|---|---|---|
| Trial pauses indefinitely at G2C | Operator verdict not yet issued; Marcus is checkpoint-paused per HIL discipline | Issue verdict via your transport (Step 5) |
| `GateError("digest_mismatch")` on verdict submit | Decision-card-digest copied incorrectly OR card was re-emitted | Re-fetch the current card; copy digest exactly; re-submit |
| `OverrideTokenStaleError` on apply_override | Token expired (>5 min since submit_override) | Re-run Phase 1 to get fresh token; re-apply within 5 min |
| Live API calls fail with no key | `WONDERCRAFT_API_KEY` / `ELEVENLABS_API_KEY` absent | Add to `.env`; restart trial; OR accept skipped specialists per pytest.skip pattern |
| Sanctum-mutation warning in DecisionCard meta | You edited a file under `_bmad/memory/<sanctum>/` mid-trial | Expected per FR59 NFR-O3 non-fatal; consider whether cache invalidation is acceptable; if yes, proceed; if no, restart trial |
| Replay drift on second invocation of same trial | Sanctum content changed OR pack-version bumped between runs | Use `--mode warn-on-clone` to inspect drift detail; re-baseline if drift is intentional |

---

## See also

- [`docs/operator/conditional-gate-addendum-playbook.md`](conditional-gate-addendum-playbook.md) — Operator-window workflows for M2 (Wondercraft) + M3 (Texas) conditional gates
- [`docs/operator/post-m5-runbook.md`](post-m5-runbook.md) — Post-M5 verdict-path operational guide (now actualized to SHIP-CONDITIONAL state)
- [`docs/dev-guide/langgraph-migration-guide.md`](../dev-guide/langgraph-migration-guide.md) — Architectural deep-dive
- [`README.md`](../../README.md) — Project orientation
- [`docs/operator/hud-guide.md`](hud-guide.md) — HUD panels, watch mode, active-trial/cost interpretation
- **Live trial monitoring today:** LangSmith UI (`https://smith.langchain.com/`, workspace `course-content-production`) gives you the live trace tree per trial; `tail -f state/config/runs/<trial-id>/cost-report.md` gives running cost.
- [`docs/operator/adhoc-mode.md`](adhoc-mode.md) — runtime single-prompt Marcus exploration without trial registration
