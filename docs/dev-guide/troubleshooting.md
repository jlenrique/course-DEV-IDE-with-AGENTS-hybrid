# Troubleshooting — Common Issues + Resolutions

**Audience:** Operators running trials + dev agents extending the migration.
**Authored:** 2026-04-26 (post-Slab-3-close runway prep).

Quick-reference for issues you'll likely hit. Issues organized by surface — run `Ctrl+F` on the symptom you're seeing.

---

## Sanctum / Cold-Read Issues

### Symptom: `_read_marcus_sanctum_digest()` returns empty string

**Likely cause:** `_bmad/memory/bmad-agent-marcus/` directory is empty OR doesn't exist OR allowlist files missing.

**Diagnosis:**
```bash
ls _bmad/memory/bmad-agent-marcus/
.venv/Scripts/python.exe -c "from marcus.facade import get_facade; f = get_facade(); print(f.state.marcus_fingerprint)"
```

**Resolution:**
- If dir absent: operator runs Marcus First Breath ceremony per `skills/bmad-agent-marcus/SKILL.md` activation sequence
- If dir present but empty: graceful-degrade per FR30 (cold-read returns empty digest); cache-prefix discipline still works but Marcus operates without persona context
- If files present but allowlist mismatch: check `_read_marcus_sanctum_digest` allowlist source (`skills/bmad-agent-marcus/SKILL.md` activation-files block per A-R4-3.1)

### Symptom: Sanctum mutation warning appears in DecisionCard mid-trial

**Likely cause:** You edited a file under `_bmad/memory/<sanctum>/` while a trial was active. Sanctum-watcher (Slab 4.6) detected the change and emitted a `kind="sanctum_mutation"` ledger event + `sanctum_warnings` enrichment.

**Resolution per NFR-O3 (non-fatal):**
- Trial continues; cache_state may transition `healthy` → `mixed`
- Inspect `meta.sanctum_warnings` in next DecisionCard for the mutated file path + suggested invalidating commit
- If mutation was intentional: accept the cache invalidation; trial proceeds
- If mutation was accidental: revert the sanctum file; cache prefix may re-stabilize at next trial cold-read

### Symptom: Wanda sanctum CLONE-FORK-NOTICE.md test fails

**Likely cause:** Fresh clone — `_bmad/memory/wanda-sidecar/CLONE-FORK-NOTICE.md` doesn't exist locally because `_bmad/` is gitignored per project_no_docker convention.

**Resolution:**
```bash
# Author the notice locally (not committed):
cat > _bmad/memory/wanda-sidecar/CLONE-FORK-NOTICE.md <<EOF
# CLONE-FORK-NOTICE

Fork commit SHA: 3ed7c56
Fork date: 2026-04-24 (severance per MEMORY.md::project_upstream_severance)
Sanctum authored in clone post-Slab-2c.2.
Backports stop after Slab 1 close per FR60.
EOF
```

---

## Postgres / Database Issues

### Symptom: `psycopg.OperationalError: connection failed` during preflight or test runs

**Likely cause:** `DATABASE_URL` env var unset OR Postgres not running OR auth misconfig.

**Diagnosis:**
```bash
echo $env:DATABASE_URL  # PowerShell; should print non-empty
# OR
echo $DATABASE_URL     # Bash

# Test connection
.venv/Scripts/python.exe -c "import os, psycopg; psycopg.connect(os.environ['DATABASE_URL'], connect_timeout=5).close(); print('OK')"
```

**Resolution per CLAUDE.md `project_no_docker` convention:**
- Postgres runs natively on host (NOT Dockerized)
- Verify Postgres service is up (`pg_isready` or platform equivalent)
- Verify `DATABASE_URL` matches your local Postgres setup (typically `postgresql://user:pass@localhost:5432/course_dev_ide_migration`)
- Verify `pg_hba.conf` allows local connections + the user has connect permission on the database
- Pre-flight degrades to WARN (not FAIL) on missing DATABASE_URL — trial-run can use in-memory checkpointer (Slab-1 substrate); degraded mode acceptable for first-trial experimentation

### Symptom: `ledger_events` table not found

**Likely cause:** Slab 4.4 schema not yet loaded into Postgres.

**Resolution:**
```bash
psql $env:DATABASE_URL -f app/ledger/schema.sql
```

Re-run preflight to confirm: `_check_postgres()` should report `PASS: Postgres reachable + ledger_events table loaded`.

---

## LangChain / LangGraph Issues

### Symptom: `ImportError: No module named 'langgraph'` (or langchain, langsmith, fastapi, etc.)

**Likely cause:** Deps not installed in current `.venv` (pre-Slab-3-runway-prep state).

**Resolution:**
```bash
# Install editable + dev extras (covers all migration deps per pyproject.toml extension)
.venv/Scripts/python.exe -m pip install -e ".[dev]"

# OR via uv (if installed)
python -m pip install -e ".[dev]"  # (uv sync is disabled: [tool.uv] managed=false)
```

Verify via preflight: `_check_postgres` + `_check_mcp_servers` + dashboard import-linter check should all pass.

### Symptom: LangSmith traces not appearing in dashboard

**Likely cause:** `LANGSMITH_TRACING=true` env var not set OR `LANGSMITH_API_KEY` absent.

**Resolution:**
```bash
# Add to .env
LANGSMITH_API_KEY=<your-key>
LANGSMITH_PROJECT=course-dev-ide-migration
LANGSMITH_TRACING=true  # critical — enables tracing
```

Restart trial; traces should appear at `https://smith.langchain.com/projects/course-dev-ide-migration`.

---

## DecisionCard / Verdict Issues

### Symptom: `GateError("digest_mismatch")` on verdict submit

**Likely cause:** The `decision_card_digest` you submitted doesn't match the digest emitted by Marcus on the current card. Either you copied the digest incorrectly, OR the card was re-emitted (rare — usually means trial state shifted between card-emission and verdict-submit).

**Resolution:**
1. Re-fetch the current DecisionCard for `(trial_id, gate_id)` via your transport
2. Copy the `decision_card_digest` field exactly (sha256-hex shape; no whitespace)
3. Re-submit verdict with the fresh digest

Per Story 3.3 W-R1-3.3-2 anti-replay binding: digest is bound to `(card_content + trial_run_id + issuance_timestamp + server_nonce)` — cross-trial replay also blocked.

### Symptom: `OperatorVerdict` cross-field validator failure: `edit_payload required iff verb == "edit"`

**Likely cause:** You set `verb="edit"` but didn't supply `edit_payload`, OR you supplied `edit_payload` with verb `approve`/`reject`.

**Resolution:** verbs and payloads must match:
- `verb=approve` → omit `edit_payload`
- `verb=edit` → supply `edit_payload` (JSON object describing the proposed edit)
- `verb=reject` → omit `edit_payload`

### Symptom: `OverrideTokenStaleError` on `apply_override`

**Likely cause:** `confirm_token` from Phase 1 (`submit_override`) expired (>5 min since issuance).

**Resolution:** re-run `submit_override` to get a fresh token; apply within 5 min:
```bash
# Phase 1 — fresh token (NO state mutation)
.venv/Scripts/python.exe -m marcus.cli override submit \
    --trial-id <id> --node-id <node> --new-model <model>
# Phase 2 — apply with the fresh token
.venv/Scripts/python.exe -m marcus.cli override apply \
    --trial-id <id> --confirm-token <fresh-token>
```

---

## Texas / Retrieval Issues

### Symptom: `from marcus.dispatch.contract import ...` fails

**Likely cause:** Pre-Slab-3.1 state — top-level `marcus/dispatch/contract.py` shim wasn't authored yet OR `_REPO_ROOT` not on `sys.path`.

**Resolution per Slab-3 substrate-aware adaptation:**
- Verify `marcus/dispatch/contract.py` exists at repo root (per Slab-3.1 W-R2 BLOCKER RESOLVED)
- Verify Texas's `run_wrangler.py:49-56` correctly inserts `_REPO_ROOT` into `sys.path`
- Identity invariant test: `marcus.dispatch.contract.DispatchKind is app.marcus.dispatch.contract.DispatchKind` should hold
- Run `tests/integration/marcus/test_texas_run_wrangler_imports_succeed.py` to verify

### Symptom: Texas AC-B-OP M1-M5 evidence not produced

**Likely cause:** Operator-window deferred (per `2a.4-followon-ac-b-op-live-retrieval` deferred-inventory entry). M3 verdict will remain CONDITIONAL-GREEN-PENDING-OPERATOR-ADDENDUM until resolved.

**Resolution:** see [`docs/operator/conditional-gate-addendum-playbook.md`](../operator/conditional-gate-addendum-playbook.md) §M3 for the helper-script invocation + paste workflow.

---

## Marcus / Orchestration Issues

### Symptom: `get_facade()` returns different instance each call

**Likely cause:** This is BY DESIGN per Story 3.1 Decision #5 Option C (pure re-read each call; NO singleton). FR30 cold-read sanctum discipline; no in-memory continuity.

**NOT a bug.** Operator should expect each `get_facade()` call to:
- Re-read sanctum
- Generate fresh `session_id` UUID
- Return a new Facade instance

If you need session-scoped state, store it in `RunState` (operator-managed via verdicts) NOT in the Facade.

### Symptom: Marcus envelope baseline regression detected

**Likely cause:** Sanctum content changed OR pack-version bumped OR Marcus persona evolved between baseline capture (3.6 W-R7) and current trial.

**Resolution:**
- Inspect `tests/fixtures/marcus/baseline_envelope/<latest>/BASELINE_METADATA.md` for capture-environment hash
- If drift is intentional (post-Slab-4 expansion): re-baseline per Decision #6 W-R1-3.6-2 re-baseline protocol (party-mode gated, version-bumped fixture migration)
- If drift is unintentional: investigate sanctum content + pack-version diff; revert if accidental

### Symptom: `app/marcus/` vs `marcus/` confusion

**Likely cause:** Slab-3 substrate-aware adaptation INVERTED the planned architectural model. Canonical Marcus home is **`marcus/`** (top-level; Story 30-1 lesson-planner package + Slab-3 additive `marcus/dispatch/contract.py` + `marcus/orchestrator/{supervisor,routing}.py`). `app/marcus/` is the Slab-1 namespace stub (kept for backward-compat per `app.marcus.*` import-linter rules; possible retirement post-M5 per `migration-tech-debt-app-marcus-stub-disposition` deferred-inventory entry).

**Resolution:** when authoring new code, prefer `marcus/` for orchestrator + intake + facade work; prefer `app/` for models, gates, ledger, runtime, specialists. See `docs/dev-guide.md` §Migration Dev Appendix architectural map for the full layout.

---

## Trial-Run Issues

### Symptom: Trial pauses indefinitely at G2C (or any gate)

**Likely cause:** Operator verdict not yet issued; Marcus is checkpoint-paused per HIL discipline.

**Resolution:** issue verdict via your transport per `docs/operator/trial-run-runbook.md` Step 5.

### Symptom: §01-§15 step IDs don't match trial output

**Likely cause:** `pipeline-manifest.yaml` uses step IDs by NAME not ordinal (e.g., `01`, `02`, `02A`, `04A`, `04.5`, `04.55`, `4.75`, ...). The "§01-§15" framing is from epic 3.6 wording; actual manifest has 33+ nodes with non-sequential ID prefixes.

**Resolution:** consult `state/config/pipeline-manifest.yaml::nodes[*].id` for actual step IDs; reference by name (`02A`, `04.5`, etc.) not ordinal in operator commands or evidence pastes.

### Symptom: Trial-replay regression test fails on a previously-closed trial

**Likely cause:** Sanctum content changed since the trial closed OR pack-version bumped OR a Slab-X substrate change retroactively invalidates the replay.

**Resolution per architecture D1:**
- Run with `--mode warn-on-clone` instead of `--mode fail-loud` to inspect drift detail without failing
- Inspect `ReplayError` discriminated subclass: `PackHashDriftError` / `SanctumFingerprintDriftError` / `ManifestSnapshotDriftError`
- If drift is intentional (post-substrate evolution): re-baseline OR exclude trial from replay coverage with rationale

---

## Test / CI Issues

### Symptom: `test_temp_pyproject_baseline_is_5_rows` fails (or related generator C3-row fixture tests)

**Likely cause:** RESOLVED at Tier-1-A cleanup 2026-04-26 (commit `aff8e2b`). Fixture asserted hardcoded 5 rows but baseline grew to 7 post-Slab-3.3 gate-bridge entries. If still seeing this on your branch, you're behind the cleanup commit; rebase or pull.

### Symptom: `test_no_env_example_in_repo` fails (or related .env-template tests)

**Likely cause:** RESOLVED at Tier-1-A cleanup 2026-04-26. Migration policy explicitly inverted primary's "no .env templates in-tree" — `.env.example` IS the canonical operator template now. If still seeing this on your branch, rebase or pull.

### Symptom: 8 PipelineManifest collection errors at pytest collection time

**Likely cause:** RESOLVED at Codex Slab-4.1 close — those 8 collection errors went 8→0 after Codex's check_manifest_lockstep.py work. If still seeing on your branch, you're pre-Slab-4.1.

### Symptom: Pre-existing test failures in `tests/contracts/test_33_*` cluster

**Likely cause:** 4 of the 9 remaining pre-existing failures filed as `pre-slab-3-cleanup-33-*` deferred-inventory entries (template prose drift; v42 hand-edit; manifest stub key collision; 30-1 zero-edit invariant). NOT trial-run-blocking; post-M5-ship cleanup candidates.

**Resolution:** see `_bmad-output/planning-artifacts/deferred-inventory.md` §"Pre-existing test-failure cleanup follow-ons" for per-entry triage path.

---

## Environment / Setup Issues

### Symptom: Fresh clone — bootstrap script fails on Python version

**Likely cause:** Python <3.11 on PATH. Per `pyproject.toml::requires-python = ">=3.11"`.

**Resolution:** install Python 3.11+ from python.org or via system package manager; verify `python --version` shows ≥3.11.

### Symptom: `pre-commit install` fails or hooks don't fire

**Likely cause:** `pre-commit` not installed OR `.pre-commit-config.yaml` syntax issue.

**Resolution:**
```bash
.venv/Scripts/python.exe -m pip install pre-commit
.venv/Scripts/pre-commit install
.venv/Scripts/pre-commit run --all-files  # smoke test
```

### Symptom: `lint-imports` reports BROKEN contracts

**Likely cause:** A code change violated one of the 9 import-linter contracts (Marcus M1-M4 + C3 + Cora C1+C2 + scheduler-forbidden + lane-isolation).

**Resolution:** read the BROKEN contract names + violating modules from `lint-imports` output; either revert the import OR (if intentional architectural change) update the contract per architecture decision-of-record + party-mode consensus.

### Symptom: Ruff reports 998 errors on fresh check

**Likely cause:** Pre-existing legacy debt (per `migration-tech-debt-ruff-cleanup` deferred-inventory entry). NOT trial-run-blocking; CI does NOT fail on these.

**Resolution:** if you want a clean local lint state, run `.venv/Scripts/python.exe -m ruff check app/ tests/ skills/ scripts/ marcus/ --fix` (auto-fixes a subset). For full cleanup, see post-M5-ship `migration-tech-debt-ruff-cleanup` story.

---

## Where to file new issues

If you hit something not in this troubleshooting guide:

1. **First-time / not-sure-where-it-fits:** add a candidate entry to `_bmad-output/planning-artifacts/deferred-inventory.md` per CLAUDE.md §"Deferred inventory governance" §3
2. **Substrate gap:** file as `migration-tech-debt-<short-name>` follow-on
3. **Bug in shipped code:** file as `migration-bugfix-<short-name>` follow-on with severity classification (blocker / high / medium / low)
4. **Documentation gap:** add to this troubleshooting.md OR appropriate guide; file PR

---

## See also

- [`docs/operator/trial-run-runbook.md`](../operator/trial-run-runbook.md) — first-trial step-by-step
- [`docs/operator/conditional-gate-addendum-playbook.md`](../operator/conditional-gate-addendum-playbook.md) — M2/M3/M4 operator-window addenda
- [`docs/operator/post-m5-runbook.md`](../operator/post-m5-runbook.md) — per-verdict-path operations
- [`docs/dev-guide/specialist-anti-patterns.md`](specialist-anti-patterns.md) — A1-A14+ harvested anti-patterns (FR64 catalog)
- [`scripts/utilities/trial_run_preflight.py`](../../scripts/utilities/trial_run_preflight.py) — 12-point readiness sweep
- [`scripts/utilities/migration_health_dashboard.py`](../../scripts/utilities/migration_health_dashboard.py) — single-pane status
- [`README.md`](../../README.md) — top-of-repo orientation
- [`CLAUDE.md`](../../CLAUDE.md) — BMAD project instructions + sprint governance + sandbox-AC discipline
