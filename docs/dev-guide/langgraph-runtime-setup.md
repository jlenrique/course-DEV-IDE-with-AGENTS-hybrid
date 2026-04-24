# LangGraph Runtime Setup

> **Status:** Slab 1 substrate polished at Story 1.7 close. Operator cookbook for the
> migration's cold-start ramp: clone → venv → uv install → init_postgres → smoke →
> runtime_server. Transport-parity matrix accurate as of Slab 1 close; the MCP column
> reflects the 1.1d parity test result (20/20 hot+cold runs at 0% flake).

## Cold-start sequence

Start from a fresh clone of the hybrid repo at branch
`dev/langchain-langgraph-foundation`. Assumes Python 3.12+ on PATH, native Postgres
15+ installed per [`local-postgres-setup.md`](local-postgres-setup.md) (no Docker —
the migration's `project_no_docker` decision is recorded in the operator memory index).

```bash
git clone --branch dev/langchain-langgraph-foundation <hybrid-repo-url>
cd course-DEV-IDE-with-AGENTS-hybrid

# Create and populate the venv from the lockfile.
python -m venv .venv
.venv/Scripts/python.exe -m pip install --upgrade pip
.venv/Scripts/python.exe -m pip install -r requirements.lock
.venv/Scripts/python.exe -m pip install -e .[dev]

# Populate .env from the template; at minimum, DATABASE_URL is required for
# full smoke + Slab 3+ specialist work. OPENAI_API_KEY is required at Slab 3+
# specialist invocation; Slab 1 substrate accepts the placeholder sentinel.
cp .env.example .env
# Edit .env with your local Postgres credentials + API keys.

# Bootstrap the database (idempotent).
psql "$DATABASE_URL" -f scripts/dev/init_postgres.sql

# Substrate smoke — byte-equivalent to the 1.1c contract.
.venv/Scripts/python.exe -m app.smoke_test
# Expected: smoke ok (nodes=1, payload={...})

# Full 33-node v4.2 manifest smoke — end-to-end §01→§15 through passthrough stubs.
.venv/Scripts/python.exe -m app.smoke_test --full
# Expected: smoke ok (full, nodes=33, payload={...})

# Boot the FastAPI runtime server (127.0.0.1-only bind per NFR-S2).
.venv/Scripts/python.exe -m app.runtime.server
```

## Transport Parity Contract — at-a-glance matrix

The migration runtime exposes the same minimal LangGraph node behind three transports
per architecture decision **D7** (Operator-surface contract — three-transport parity)
and **FR2** (compound MCP + FastAPI + CLI substrate). Each cell answers one question:
*does this transport have the corresponding artifact landed yet?*

|                          | FastAPI                | MCP                              | CLI                |
| ------------------------ | ---------------------- | -------------------------------- | ------------------ |
| **Code present**         | ✅ 1.1c                | ✅ 1.1c                          | ⏳ Slab 3 Story 3.4 |
| **Smoke test (per-PR)**  | ✅ 1.1c                | — (not per-PR by design)         | ⏳ Slab 3           |
| **Smoke test (nightly / on-merge)** | — (covered per-PR) | ✅ 1.1d (20/20 at 0% flake) | ⏳ Slab 3           |
| **Parity acceptance**    | — (parity is two-transport at M1) | ✅ 1.1d (M1 gate green) | ⏳ Slab 3 (3.4) |

**Reading the matrix:** rows are artifact kinds; columns are transports. A `✅` means
the artifact is on disk and exercised at the cited story. A `—` means *N/A by design*
(with the design rationale in the cell). A `⏳` means deliberately deferred to a
downstream slab.

## MCP transport — Slab 1 substrate vs production-ready

The MCP code substrate landed in 1.1c; nightly / on-merge stdio smoke + FastAPI↔MCP
byte-equivalent parity assertion landed in 1.1d. Both transports are M1-substrate for
the FR2 compound contract; CLI completes the three-transport claim in Slab 3 Story
3.4. The "production-ready" qualifier still depends on Slab 2 specialist migrations
exercising real workloads through these transports — Slab 1 closure is substrate,
not feature-complete.

Origin of the middle-path split (MCP code in Slab 1; MCP smoke in a sibling 1.1d
story): 2026-04-22 party-mode consensus (5/5 vote). Rationale recorded at
[`_bmad-output/planning-artifacts/slab1-story-set-A-t1-bundle.md §8`](../../_bmad-output/planning-artifacts/slab1-story-set-A-t1-bundle.md).

## Troubleshooting

### `docker: command not found`

Not an error — the migration runs Postgres natively. The earlier Story 1.1b Docker
blocker was resolved by the `project_no_docker` operator decision (see the
`memory/project_no_docker.md` entry in the operator's Claude memory index). Install
Postgres 15+ via the platform-native installer per
[`local-postgres-setup.md`](local-postgres-setup.md).

### `psql: command not found`

`psql` is only required for the one-time `init_postgres.sql` bootstrap step. If it's
not on PATH, install the Postgres client tools from your distribution or the EDB
installer. Dev-agent acceptance tests never assume `psql` on PATH — they verify via
the shipped `psycopg` Python driver and skip-on-unreachable, per the
`verify-via-shipped-deps` rule captured in the operator's Claude memory
(`memory/feedback_verify_via_shipped_deps.md`).

### `DATABASE_URL not set`

Copy `.env.example` to `.env` and fill in the Postgres credentials. The runtime server,
checkpointer, and retention-cleanup CLI all read this env var. The substrate smoke
(`python -m app.smoke_test`) does NOT require `DATABASE_URL` — the stub manifest's
passthrough smoke path is in-memory only.

### `OPENAI_API_KEY not set`

Slab 1 substrate accepts the placeholder sentinel
`"sk-substrate-no-real-key-do-not-invoke"`. Slab 3+ specialist work requires a real
key; `.invoke(...)` calls against the stub will fail loudly until the key is set. See
`app.models.adapter`.

### `pytest: command not found`

Re-install dev dependencies: `pip install -e .[dev]`. The Slab 1 lockfile does not
include dev deps by design (runtime lockfile stays minimal). Candidate deferred-inventory
follow-up: include dev deps in lockfile so `python -m pytest` works from a fresh venv
without the extra install step.

### Checkpoints not surviving restart

The checkpointer persists to Postgres per FR3; restart survival is FR4. If checkpoints
are lost across restart, verify `DATABASE_URL` points at the same Postgres instance,
`init_postgres.sql` completed, and retention cleanup hasn't run with an aggressive
`retain_failed: false` override (shipped defaults keep failed threads indefinitely).

## Related

- Database bootstrap + retention: [`local-postgres-setup.md`](local-postgres-setup.md)
- Model cascade resolution: [`model-selection-guide.md`](model-selection-guide.md)
- LangGraph state idioms: [`langgraph-state-idioms.md`](langgraph-state-idioms.md)
- Migration guide (standing reference): [`langgraph-migration-guide.md`](langgraph-migration-guide.md)
- Transport-parity envelope exceptions:
  [`transport-parity-envelope-exceptions.md`](transport-parity-envelope-exceptions.md)
