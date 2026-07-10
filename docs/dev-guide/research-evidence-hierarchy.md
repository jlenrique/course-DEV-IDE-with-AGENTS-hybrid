# Research evidence hierarchy (Agentic Research Foundations R0)

**Status:** binding taxonomy for foundations tranche (2026-07-10)  
**Epic:** `epic-agentic-research-foundations-2026-07-10.md`  
**Policy:** Prefer peer-reviewed journals; allow the full hierarchy when **credibility is explicitly surfaced** on every cited row. Never silently equate tiers.

## Hierarchy tiers (closed set for v1)

| Tier code | Label | Typical sources | Default peer_reviewed |
|-----------|-------|-----------------|------------------------|
| `T1_systematic` | Systematic review / meta-analysis / guideline | Cochrane, society guidelines | true |
| `T2_peer_rct_or_equiv` | Peer-reviewed primary research (RCT / strong design) | Indexed journals | true |
| `T3_peer_observational` | Peer-reviewed observational / mixed methods | Indexed journals | true |
| `T4_peer_other` | Other peer-reviewed (commentary, methods, letters) | Indexed journals | true |
| `T5_preprint` | Preprint / not yet peer-reviewed | medRxiv, bioRxiv, SSRN | false |
| `T6_grey_institutional` | Grey literature — institutional / government | FDA, CDC, WHO, university reports | false |
| `T7_secondary_media` | Secondary / media / blog / vendor | News, trade, marketing | false |
| `T8_unknown` | Insufficient metadata to classify | — | false |

**Preference rule:** When ranking for (a) corroborate and (c) enrich, prefer lower tier numbers (T1–T4) over T5–T8. Gap-fill (b) may accept lower tiers when higher tiers are exhausted — **must surface tier**.

## Required fields on every `research_entries` row (R4+)

| Field | Meaning |
|-------|---------|
| `evidence_hierarchy_tier` | One of the tier codes above |
| `peer_reviewed` | boolean |
| `provider_provenance` | list/string of providers that contributed (e.g. `scite`, `consensus`, `jefferson_library`) |
| `triangulation_status` | `dual_provider` \| `single_provider` \| `none` |
| `reliability_score` | optional float from triangulator (R3+); null if not computed |

## Mapping hints (providers → tier)

- Scite / Consensus journal articles with peer-review signals → T2–T4 (refine with publication type when available)  
- Systematic review keywords / study type → T1 when detectable  
- Preprint servers → T5  
- Jefferson full-text of a peer-reviewed DOI → inherit journal tier; set provenance to include `jefferson_library`  
- Unknown → T8 fail-soft with explicit flag (never invent T1)

## Non-claims

- Tier assignment is **heuristic metadata**, not a clinical grade of evidence for patient care.  
- Tier ≠ semantic claim-support (that audit is TRAIL).  
- G2 citation gate remains **resolvability**, not hierarchy enforcement.
