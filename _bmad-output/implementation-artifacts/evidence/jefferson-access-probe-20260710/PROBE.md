# Jefferson library access probe (2026-07-10) — pre-R5

> **Superseded for live conclusions by** [`../jefferson-access-probe-session3-20260710T213250Z/PROBE.md`](../jefferson-access-probe-session3-20260710T213250Z/PROBE.md) (**PASS** — real NEJM PDF via headed Playwright + Chrome cookies).  
> Intermediate reauth (curl-only): [`../jefferson-access-probe-reauth-20260710T172839Z/PROBE.md`](../jefferson-access-probe-reauth-20260710T172839Z/PROBE.md).  
> Operator later clarified this machine was **not** authenticated during the first probe window; session-backed suite ran after Chrome fully quit.

**Operator note:** No unique library credentials — Campus Key / **SSO (SAML)**. Browser logged in during probe window.

## Architecture discovered (headless + public config)

| Surface | URL / signal | Result from agent host (no SSO cookies) |
|---------|----------------|------------------------------------------|
| Library portal | `https://library.jefferson.edu/` | 200 public |
| A–Z databases | `https://jefflibraries.libguides.com/az/databases` | 200 public catalog |
| Discovery (Primo VE) | `https://jefferson.primo.exlibrisgroup.com/` `vid=01TJU_INST:01TJU` | 200 SPA; institution cookie `01TJU_INST` |
| Auth profile (Primo config) | `TJUSAML` / `authentication-system: SAML` | Confirms SSO, not API key |
| Ex Libris rewrite proxy | `https://proxy-na.hosted.exlibrisgroup.com/exl_rewrite/` | From Primo public config `Proxy_Server` |
| Guessed classic EZproxy hosts | `*.proxy1.library.jefferson.edu`, `jefferson.idm.oclc.org` | **DNS NXDOMAIN** — not the live proxy shape |
| DOI → NEJM full text | `doi.org/10.1056/NEJMoa2034577` | Cloudflare **403** challenge (no institutional session) |
| PubMed HTML | `pubmed.ncbi.nlm.nih.gov/33378609/` | 200 public page (no Jefferson OpenURL session) |
| Primo OpenURL shell | `/discovery/openurl?...&rft_id=info:doi/10.1056/NEJMoa2034577` | 200 SPA shell only (JS required; no View It JSON without browser session) |

## Implication for R5 provider design

1. **Not** `JEFFERSON_API_KEY` / Basic auth — **browser SSO session** (or future Alma API if TJU provisions an app key — not available now).  
2. Viable agent patterns: (a) headed Playwright attached to operator Chrome profile / persistent SSO context; (b) operator-assisted OpenURL resolve → capture final PDF URL + cookies for one-shot fetch; (c) Primo/Alma APIs only if institution issues keys later.  
3. Scite/Consensus remain identity/DOI spine; Jefferson = **full-text fulfillment** after DOI known.  
4. Live R5 arm = SSO browser path, not env-secret path.

## Operator live checklist (do now while logged in)

Opened tabs for you — please glance and note:

1. **Primo search** — signed in as you? Any “Sign in” still showing?  
2. Click a result → **View It / full text** — does PDF/HTML open?  
3. Copy the **address bar URL** after full text loads (look for `proxy-na.hosted.exlibrisgroup.com` or publisher host).  
4. **Scopus** from A–Z — does it open without a second password prompt?  
5. **Find Full Text** guide → try the same NEJM DOI via Jefferson button.

Paste those URL patterns back when you return — that locks the R5 adapter contract.

## Operator return (2026-07-10 ~17:11 ET)

**Post-click NEJM PDF URL (after cookie accept):**
`https://www.nejm.org/doi/pdf/10.1056/NEJMoa2034577`

**Observations:**
- Final URL is the **publisher native PDF path** — **no** `proxy-na.hosted.exlibrisgroup.com` (or classic EZproxy) visible in the address bar.
- Operator does not use/recognize “Primo” by name (Primo = Jefferson’s library search/discovery site behind the scenes).
- Headless agent curl to the same NEJM host got Cloudflare 403; operator browser (SSO + cookies) reached PDF.

**R5 design implications (updated):**
1. Do **not** key fulfillment success on “URL contains proxy hostname.” Success = **bytes are PDF / full text** (or publisher HTML with institutional access), after a library-mediated or SSO-warmed session.
2. Journey may be: library link / OpenURL / Jefferson button → SSO if needed → **publisher host** with session cookies (or on-campus IP recognition). Final URL often looks “public.”
3. Agent fulfillment options stay: headed browser with operator SSO context; or capture session cookies from a one-shot assisted resolve; not a static API key.
4. Always record provenance: `provider_provenance` includes `jefferson_library` when access was obtained via institutional path, even if final URL is `nejm.org`.
