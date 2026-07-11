# Jefferson library access probe — REAUTH (2026-07-10)

**Evidence:** `_bmad-output/implementation-artifacts/evidence/jefferson-access-probe-reauth-20260710T172839Z/`  
**Stamp:** 2026-07-10T21:30:16Z  
**Prior probe:** `jefferson-access-probe-20260710/PROBE.md` (written under mistaken “already authenticated” assumption)

## Why re-run

Operator clarified: earlier, this machine was **not** authenticated; it is now. Re-ran the full curl suite + Playwright attempts against the local Chrome profile.

## Curl suite (agent process — no browser cookie jar)

| Probe | HTTP | Result |
|---|---:|---|
| Library portal | 200 | Public OK |
| A–Z databases / Find Full Text | 200 | Public OK |
| Jefferson discovery (Primo VE) home/search/OpenURL | 200 | SPA shell OK |
| Primo public config JSON | 200 | Auth profile still `TJUSAML` / SAML |
| Classic EZproxy guesses (`proxy1…`, `idm.oclc.org`) | 000 | Still **NXDOMAIN** |
| Ex Libris rewrite root | 403 | No session |
| DOI → NEJM | 200 | Lands on `nejm.org` (CF signal; not full-text proof) |
| NEJM article HTML | 403 | Cloudflare challenge |
| **NEJM PDF** (operator’s known good URL) | 200 | Redirects to **`/action/cookieAbsent`** — **not a PDF** |
| PubMed HTML | 200 | Public page |

## Delta vs first probe

| Check | First probe | Reauth (now) |
|---|---|---|
| DOI / NEJM | Hard Cloudflare **403** | Soften to **200** on DOI landing + **`cookieAbsent`** on PDF |
| NEJM full article | 403 | Still **403** (CF) from agent |
| Proxy hostnames | NXDOMAIN | Unchanged |
| PDF bytes retrieved by agent? | No | **Still no** |

So: being “authenticated on this machine” in **Chrome** did **not** change what **curl/headless** can fetch. The decisive PDF signal is now clearer: NEJM answers `cookieAbsent` instead of only a generic bot wall.

## Playwright / Chrome SSO attempt

- Chrome is **running** (~19 processes) → `Default/Network/Cookies` is **file-locked** (Permission denied / WinError 32).
- Copied-profile launch ran **without** cookies → NEJM PDF/article = Cloudflare “Just a moment…” (403).
- Launch against the real Chrome User Data dir failed (profile lock).
- No Chrome remote-debugging port (`9222`) was open, so the agent could not attach to the live authenticated window.

## Corrected conclusion (binding for R5)

1. **SSO/SAML only** — confirmed again; no library API key path.
2. **Publisher-native PDF URL is correct** (`nejm.org/doi/pdf/...`) but **requires browser cookies**; agent curl gets `cookieAbsent`.
3. Machine login ≠ agent access. R5 must use a **headed/persistent browser session** (or CDP attach to your logged-in Chrome), not bare HTTP from the agent host.
4. Opened 4 verification tabs in your default browser (discovery search, NEJM PDF, Scopus A–Z, Find Full Text) for your eyeball check.

## To finish a true session-backed agent proof

Pick one:

1. **Briefly quit Chrome completely**, tell me, and I re-run the Playwright cookie-copy path; or  
2. Restart Chrome with remote debugging and tell me when ready:
   ```text
   chrome.exe --remote-debugging-port=9222
   ```
   (then I attach Playwright over CDP and fetch the NEJM PDF through your live session)
