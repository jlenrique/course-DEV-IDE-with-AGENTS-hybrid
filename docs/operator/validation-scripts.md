# Operator validation scripts

Quick CLI shortcuts for the operator-run validation actions across the migration's bundle + ceremonies. All scripts auto-load `.env` where credentials are needed; otherwise no setup.

All scripts live under `scripts/operator/` and run via the venv-pinned interpreter:

```
.venv\Scripts\python.exe scripts\operator\<script>.py
```

## Scripts

### Bundle validation (no live API; no credentials)

| Script | Purpose | Cost | Time |
|---|---|---|---|
| `dual_gate_slab_6_0.py` | Slab 6.0 dual-gate evidence (production envelope substrate; composition discipline) | $0 | ~5 sec |
| `bundle_health_check.py` | Slab 6 trial-experience bundle (6.2 + 6.3 + 6.4 + 6.5) focused regression | $0 | ~30 sec |
| `migration_full_health_check.py` | Full migration substrate (Slabs 6.0–6.5 + isolation + lockstep) | $0 | ~60 sec |
| `gate5_slab_6_4.py` | Slab 6.4 Gate 5 dual-gate evidence ceremony (validator + composition + strict + golden) | $0 | ~30 sec |

### Live API ceremonies (require keys; cost real money)

| Script | Required keys | Cost (typical) | Time |
|---|---|---|---|
| `dual_gate_slab_6_1.py` | OPENAI_API_KEY + LANGSMITH_API_KEY + LANGSMITH_PROJECT | ~$0.10–$0.30 | ~30 sec |
| `m2_wondercraft_ceremony.py` | WONDERCRAFT_API_KEY | ~$2.25 | ~3-5 min |
| `m3_texas_ceremony_notion.py` | NOTION_API_KEY | $0 | ~10 sec |
| `m3_texas_ceremony_scite.py` | SCITE_USER_NAME + SCITE_PASSWORD | $0 | ~30 sec |

### Diagnostic helpers

| Script | Purpose |
|---|---|
| `check_keys.py` | Verify which `.env` keys are present + expected by which surface |
| `scite_heartbeat.py` | Minimal Scite MCP connectivity probe |
| `probe_scite_mcp.py` | Auth-mode discovery on Scite MCP |
| `harvest_wondercraft_job.py` | Recover finished Wondercraft job by job_id |

## Common patterns

**Pre-trial readiness check:**
```
.venv\Scripts\python.exe scripts\operator\migration_full_health_check.py
```
Run before queuing first tracked trial OR before any composition-affecting work.

**Bundle close confidence:**
```
.venv\Scripts\python.exe scripts\operator\bundle_health_check.py
```
Run after any bundle story close to confirm no cross-story regression.

**Slab 6.4 Gate 5 ceremony (current need):**
```
.venv\Scripts\python.exe scripts\operator\gate5_slab_6_4.py
```
Prints paste-ready evidence block for Dev Agent Record §"Operator dual-gate gate-2 evidence."

**Live production trial smoke (Slab 6.1 dual-gate re-run):**
```
.venv\Scripts\python.exe scripts\operator\dual_gate_slab_6_1.py
```
Verifies live OpenAI specialist invocation through ProductionDispatchAdapter + checkpoint pause/resume end-to-end. Costs ~$0.10–$0.30 per run.

## Output convention

All scripts print a paste-ready summary block at the end suitable for direct paste into Dev Agent Record sections, deferred-inventory entries, or m5-decision waypoint annotations. Format mirrors the close-protocol patterns established at Slabs 6.0 / 6.1 / 6.2 closes.

Exit codes: 0 = PASS; non-zero = FAIL or pre-flight failure (e.g., missing keys for live ceremonies).
