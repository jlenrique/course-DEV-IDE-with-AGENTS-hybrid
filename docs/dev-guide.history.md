# dev-guide.md — archived Legacy Context

> Cold archive of the `## Legacy Context` section (pre-migration workflow + migration-status
> banners) moved out of `docs/dev-guide.md` on 2026-07-18 (guide hygiene, status-surface regime).
> Historical reference only; current product status lives in `docs/STATE-OF-THE-APP.md` §11.

---

## Legacy Context

> **Migration Status (refreshed 2026-05-07 at pre-Trial-3 cleanup S5 Tier-2):** Migration unconditionally SHIPPED 2026-04-27. Slab 7 orchestrational arc COMPLETE (7a+7b+7c closed 2026-05-01 / 2026-05-01 / 2026-05-07). Pre-Trial-3 cleanup arc S1-S6 currently in progress (S1+S2+S3+S4 closed; S5+S6 in flight). **First tracked trial (Trial-3) launches post-cleanup-close** against v5 canonical pack + post-Slab-7c substrate. v5 canonical pack: `docs/workflow/production-prompt-pack-v5-narrated-lesson-with-video-or-animation.md`. Trial methodology: `docs/trials/methodology.md`. Legacy v4.2 retained as mapping-checklist legacy-axis frozen authority.


> ## MIGRATION STATUS BANNER (refreshed 2026-04-28)
>
> **This guide reflects the PRE-MIGRATION primary-repo architecture** (Cursor IDE + prompt-pack v4.x + Three-Layer Architecture). The hybrid clone on `dev/langchain-langgraph-foundation` has **MIGRATED** to LangChain/LangGraph: migration **unconditionally SHIPPED** 2026-04-27 (commit `97842ac`); Slab 6 trial-experience bundle 3/3 CLOSED 2026-04-28 (Step 02A defaults + Irene Pass 2 authoring template + HUD per-step expandable summaries); first tracked trial UNBLOCKED. The migrated runtime carries: Marcus orchestrator + production-graph runner consuming Slab 6.0 envelope substrate + 14 scaffold-conformant specialists + HIL DecisionCard gates (G1/G2C/G3/G4) with FR34 tamper-evidence + checkpoint pause/resume verified end-to-end + learning ledger + standing governance discipline (Composition Specification + Substrate Inventory Checklist N1–N12 + anti-pattern catalog A1–A17 + P1–P3).
>
> **For migration-aware developer architecture, see:**
> - **[`docs/dev-guide/langgraph-migration-guide.md`](dev-guide/langgraph-migration-guide.md)** — authoritative migration architecture + per-Slab walkthroughs + §6 Lockstep CI + §7 Frozen-Graph Ceremony
> - **[`docs/dev-guide/specialist-migration-template.md`](dev-guide/specialist-migration-template.md)** v2.4 — R1-R14 rules for per-specialist migration stories
> - **[`docs/dev-guide/specialist-anti-patterns.md`](dev-guide/specialist-anti-patterns.md)** — A1–A17 + P1–P3 catalog (substrate-level + process anti-patterns harvested across migration cycles)
> - **[`docs/dev-guide/pydantic-v2-schema-checklist.md`](dev-guide/pydantic-v2-schema-checklist.md)** — 14 idioms binding for schema-shape stories
> - **[`docs/dev-guide/scaffolds/schema-story/`](dev-guide/scaffolds/schema-story/)** — four-file-lockstep recipe
> - **[`docs/dev-guide/composition-specification.md`](dev-guide/composition-specification.md)** — Option B governing reference (envelope + adapter + composition discipline; §10 Decision Log + §11 Migration Triggers)
> - **[`docs/dev-guide/substrate-inventory-checklist.md`](dev-guide/substrate-inventory-checklist.md)** — N1–N12 standing pre-flight for substrate-affecting work
> - **[`docs/dev-guide/sources-of-truth.md`](dev-guide/sources-of-truth.md)** — comprehensive SSOT registry per topic with lockstep partners + change protocols
> - **[`docs/dev-guide/how-to-add-a-specialist.md`](dev-guide/how-to-add-a-specialist.md)** — single consolidated walkthrough from first-breath sanctum through formal close
> - **[`_bmad-output/planning-artifacts/architecture-langchain-langgraph-migration.md`](../_bmad-output/planning-artifacts/architecture-langchain-langgraph-migration.md)** — D1-D13 architecture decisions of record
> - **[`_bmad-output/planning-artifacts/epics-langchain-langgraph-migration.md`](../_bmad-output/planning-artifacts/epics-langchain-langgraph-migration.md)** — Slab 1-5 epic structure (M1-M5 milestones)
> - **[`README.md`](../README.md)** — top-of-repo project orientation + status-by-slab + migration-master-status enum
> - **[`CLAUDE.md`](../CLAUDE.md)** — BMAD project instructions + sprint governance + sandbox-AC discipline + Marcus-first activation
> - **[Migration Dev Appendix](#migration-dev-appendix)** below — migration-specific extension points added post-Slab-3 close
>
> **Scope of this legacy content (post-SHIP):** Three-Layer Architecture + state management + extension points described below are HISTORICAL REFERENCE for the pre-migration primary-repo codebase. They are NOT authoritative for migration-native development. For migrated-runtime architecture and extension points, consult the migration-aware see-also list above. This guide is preserved to keep audit-trail continuity from pre- to post-migration; it does not describe how the shipped LangGraph platform works today.

---

**Audience:** Developers building, extending, and maintaining the collaborative intelligence platform.
**Last Updated:** 2026-04-16 | **Project Phase:** Epics 1–14 complete; Waves 1–3 complete (Epics 19–21, 23); Wave 2B + `20c-15` estimator closed; `22-2` closed; prompt-pack family: v4.1 (standard), v4.2/v4.2f (motion + extraction guards), v4.3 (cluster + interstitial)

---
