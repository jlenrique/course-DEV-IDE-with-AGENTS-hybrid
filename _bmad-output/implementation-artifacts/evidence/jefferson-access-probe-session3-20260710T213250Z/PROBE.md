# Jefferson library access — SESSION-BACKED PASS (2026-07-10)

**Evidence:** `_bmad-output/implementation-artifacts/evidence/jefferson-access-probe-session3-20260710T213250Z/`  
**Result:** **PASS** — real NEJM PDF bytes retrieved via headed Playwright using the operator’s Chrome cookie store (Chrome fully quit).

## What worked

| Step | Result |
|---|---|
| Chrome quit | 0 `chrome` processes; cookie DB readable |
| Copy `Default/Network` (+ Preferences) into temp profile | OK |
| Headed Chromium `channel=chrome` + persistent context | OK |
| Navigate `nejm.org/doi/pdf/10.1056/NEJMoa2034577` | 200 |
| In-page `fetch(..., credentials:'include')` | **`application/pdf`**, **771,183 bytes**, magic `%PDF-1.3` |
| Network listener capture | PDF hits up to **906,022 bytes** saved as `captured-*.pdf` / `nejm-page-fetch.pdf` |

Saved artifacts:
- `nejm-page-fetch.pdf`
- `captured-2.pdf` / `captured-3.pdf` / `captured-4.pdf`
- `verdict.json`, screenshots

## What still fails (important for R5)

| Path | Result |
|---|---|
| Bare curl / agent HTTP (no browser cookies) | `cookieAbsent` / Cloudflare |
| Playwright `context.request.get(PDF_URL)` (APIRequestContext) | Cloudflare **403** “Just a moment…” |
| Headless without cookie copy | Cloudflare / no PDF |

So institutional full-text is **browser-session-bound**, not “machine IP alone” and not “any HTTP client with a User-Agent.”

## Corrected architecture for R5

1. Auth = **SSO cookies in a real browser profile** (SAML/`TJUSAML`), not an API key.  
2. Success criterion = **PDF/full-text bytes** (or publisher HTML with access), even when final URL is plain `nejm.org`.  
3. Working agent pattern (proven here):  
   - operator SSO in Chrome once  
   - Chrome quit (or CDP attach)  
   - headed Playwright persistent context seeded from Chrome `Network` cookies  
   - page-context `fetch` / navigation (not bare `APIRequestContext`)  
4. Provenance: stamp `jefferson_library` when access came from this institutional session path.

## Relation to earlier probes

| Probe | Verdict |
|---|---|
| `jefferson-access-probe-20260710` | Pre-auth misunderstanding; curl-only |
| `jefferson-access-probe-reauth-*` | Curl still no PDF; cookies locked while Chrome running |
| `jefferson-access-probe-session-*` (v1) | Misread Chrome PDF-viewer HTML shell as failure |
| **`session3` (this)** | **PASS — real PDF** |

## Operator note

You can reopen Chrome now.
