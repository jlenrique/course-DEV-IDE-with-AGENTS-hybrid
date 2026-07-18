# admin-guide.md — archived Legacy Context

> Cold archive of the `## Legacy Context` section (pre-migration workflow + migration-status
> banners) moved out of `docs/admin-guide.md` on 2026-07-18 (guide hygiene, status-surface regime).
> Historical reference only; current product status lives in `docs/STATE-OF-THE-APP.md` §11.

---

## Legacy Context

> **Migration Status (refreshed 2026-05-07 at pre-Trial-3 cleanup S5 Tier-2):** Migration unconditionally SHIPPED 2026-04-27. Slab 7 orchestrational arc COMPLETE (7a+7b+7c closed 2026-05-01 / 2026-05-01 / 2026-05-07). Pre-Trial-3 cleanup arc S1-S6 currently in progress (S1+S2+S3+S4 closed; S5+S6 in flight). **First tracked trial (Trial-3) launches post-cleanup-close** against v5 canonical pack + post-Slab-7c substrate. v5 canonical pack: `docs/workflow/production-prompt-pack-v5-narrated-lesson-with-video-or-animation.md`. Trial methodology: `docs/trials/methodology.md`. Legacy v4.2 retained as mapping-checklist legacy-axis frozen authority.


> ## MIGRATION STATUS BANNER (refreshed 2026-04-28)
>
> **This guide reflects the PRE-MIGRATION primary-repo workflow** (Cursor IDE + prompt-pack v4.x + per-Epic-1-24 architectural model). The hybrid clone on `dev/langchain-langgraph-foundation` has **MIGRATED**: migration unconditionally SHIPPED 2026-04-27 (commit `97842ac`); Slab 6 trial-experience bundle 3/3 CLOSED 2026-04-28; first tracked trial UNBLOCKED.
>
> **For migration-native admin operations (post-SHIP), see:**
> - **[`docs/operator/production-trial-playbook.md`](operator/production-trial-playbook.md)** — start-to-stop production-run playbook including environment confirmation + pre-flight + health-check sections at action-by-action granularity (in-progress fill during first tracked trial).
> - **[`docs/operator/validation-scripts.md`](operator/validation-scripts.md)** — operator-run validation script catalog (5 validation + 4 ceremony scripts; check_keys + dual-gate re-runs + bundle health + full health check + M2/M3 ceremonies).
> - **[`docs/operator/trial-run-runbook.md`](operator/trial-run-runbook.md)** — first-trial setup + transport choice + verdict workflow.
> - **[`README.md`](../README.md)** — top-of-repo project orientation + status + quick-start.
> - **[`.env.example`](../.env.example)** — REQUIRED/RECOMMENDED/OPTIONAL env-var categorization.
> - **[`scripts/utilities/trial_run_preflight.py`](../scripts/utilities/trial_run_preflight.py)** — 12-point readiness sweep.
> - **[`scripts/setup/first_clone_bootstrap.{ps1,sh}`](../scripts/setup/)** — one-command operator setup.
> - **[`docs/dev-guide/local-postgres-setup.md`](dev-guide/local-postgres-setup.md)** — native Postgres setup (NOT Dockerized per operator preference).
> - **[Migration Admin Appendix](#migration-admin-appendix)** below — migration-specific admin ops added post-Slab-3 close.
>
> **Scope of this legacy content (post-SHIP):** environment setup + API-key management + MCP server config + Python env + content directory layout sections described below are HISTORICAL REFERENCE for the pre-migration primary-repo. Some sections (Python env; .env management; MCP transport) carry forward to migration; others (prompt-pack management; per-Epic admin) are pre-migration only. For migration-native admin, consult the see-also list above.

---

**Audience:** System administrators and the project owner responsible for environment setup, tool connectivity, and operational health.
**Last Updated:** 2026-04-12 (migration banner actualized 2026-04-26) | **Project Phase:** Epics 1–14 complete (primary); hybrid clone is M5 SHIP-CONDITIONAL through 2026-05-03.

---
