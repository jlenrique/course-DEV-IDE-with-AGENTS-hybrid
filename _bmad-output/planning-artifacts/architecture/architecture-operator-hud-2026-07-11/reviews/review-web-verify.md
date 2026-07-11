# Review — Web-Verification / Reality-Check Audit (finalize reviewer #1)

- **Target:** `ARCHITECTURE-SPINE.md` + `.memlog.md` (version) entries, architecture-operator-hud-2026-07-11
- **Reviewer lens:** every committed decision web-researched or reality-checked, not asserted from training data
- **Date:** 2026-07-11
- **Verdict:** APPROVE WITH CORRECTIONS — the spine is unusually well reality-checked (repo pins verified against `pyproject.toml`, phone-push mechanism genuinely web-researched, brownfield claims swept by subagent), but three High findings need fixing before dev: the AD-2 atomic-write rule ignores a verified Windows concurrent-reader failure mode, the AD-6 ETag/304 poll contract silently assumes framework behavior FastAPI/Starlette does not provide, and the memlog's Apprise "(version) verified current" record is factually wrong (current is 1.12.0, not 1.9.8).

---

## 1. Verification matrix

Every named technology/version in the Stack table and ADs, classified: **(a)** verified against repo (`pyproject.toml` / venv sweep memlog entries), **(b)** verified via memlog web-research entries, **(c)** merely asserted → re-verified by this review on 2026-07-11.

| Item | Spine claim | Class | Status |
| --- | --- | --- | --- |
| Python | `>=3.11 (repo pin)` | (a) | ✅ matches `pyproject.toml` `requires-python = ">=3.11"` |
| Pydantic | `>=2.7,<3 (repo pin)` | (a) | ✅ matches pyproject |
| FastAPI / uvicorn | `>=0.136,<1` / `>=0.45,<1` "already deps" | (a) | ✅ matches pyproject; memlog sweep confirmed installed venv (server.py + gate_endpoint already run on them) |
| requests | `>=2.31,<3` "already dep" | (a) | ✅ matches pyproject (but see LOW-2: "Pushover POST" annotation conflicts with AD-9's Apprise mandate) |
| jsonschema | `>=4` "already dep" | (a) | ⚠️ it is a **dev optional extra** (`[project.optional-dependencies].dev`), pinned `>=4.0,<5` — see LOW-1 |
| Apprise | `>=1.9.8,<2` "new dep [ASSUMPTION]", memlog: "v1.9.8 (2026-07-04) verified current 2026-07-11" | (b)→re-checked | ❌ memlog record wrong — see HIGH-3. Latest on PyPI is **1.12.0, released 2026-07-04**; 1.9.8 was released **2026-03-08**. Pin range still resolves to 1.12.0, so functionally survivable |
| Apprise Pushover URL format | "Apprise URL strings … primary Pushover" | (c)→verified | ✅ current: `pover://{user_key}@{token}[/{device}]?priority=…` (priority low/moderate/normal/high/emergency, emergency takes retry+expire) — Apprise wiki Notify_pushover |
| Apprise ntfy URL format | "fallback ntfy" | (c)→verified | ✅ current: `ntfy://{topic}` (hosted ntfy.sh), `ntfys://…`, `ntfy://{user}:{password}@{host}/{topics}`, priority max/high/default/low/min — Apprise wiki Notify_ntfy |
| Pushover API | alive; priority −2..2; May-2026 quota change | (b)→re-checked | ✅ accurate: per-account pooling of 10k free msgs/month effective **2026-05-01** (blog.pushover.net "app-limits"); API stable |
| ntfy | actively maintained, hosted-tier caveats | (b) | ✅ plausible + Apprise integration current; caveats informed a fallback choice only, no spine rule depends on them |
| ETag/If-None-Match semantics | poll with If-None-Match, "re-renders only on 200" | (c)→verified | ⚠️ HTTP semantics correct, but the 304 side is NOT free in FastAPI — see HIGH-2 |
| FastAPI GET-only route pattern | GET routes only, no mutation | (c) | ✅ trivially supported; no version risk |
| `os.replace` atomicity (Windows 11/NTFS) | "Writes are atomic (temp file + os.replace)" | (c)→verified | ⚠️ pattern is the correct primitive, but a verified Windows failure mode is unhandled — see HIGH-1 |
| Port 8791 / 600s stall budget / `trial hud` CLI | defaults | — | ✅ properly `[ASSUMPTION]`-tagged; story-level correctable; no verification owed |
| Greenfield starter defaults | — | — | N/A — the spine leans on no starter/scaffold generator; brownfield substrate claims (choke-point line numbers, import-linter fence, shape-pin patterns) were verified by the recorded Explore sweep |

---

## 2. Findings

### Critical

None.

### High

**HIGH-1 — AD-2/Conventions: `os.replace` on Windows fails with `PermissionError` while any reader holds the destination open; no writer retry rule exists.**
Verified guidance (Python `os.replace` → `MoveFileExW(MOVEFILE_REPLACE_EXISTING)`; python-atomicwrites #25; golang/go #8914 discussion of the same Win32 primitive): temp-file + `os.replace` is the right same-volume atomic pattern on NTFS — readers see old-complete or new-complete, never a torn file. **But** CPython opens files without `FILE_SHARE_DELETE`, so if the HUD server (serving `/projection`), the notifier's projection watcher, or any golden-fixture test has the file open at the instant the runner replaces it, `os.replace` raises `PermissionError` (sharing violation). The spine wires *multiple* readers polling every 2–5s against a writer emitting at every state transition on Windows 11 — collision is a when-not-if over a long run, and the write sits inside `_persist_envelope` in the production runner's critical path. **Fix:** add to AD-2 (or Consistency Conventions) a bounded retry-with-tiny-backoff on the projection `os.replace` (e.g., ~5 attempts, 10–50 ms), and state that a projection-write failure after retries must not crash the runner (log + continue; run.json already persisted). Symmetric convention for readers: open-read-close immediately, never hold the handle across the poll interval.

**HIGH-2 — AD-6: FastAPI/Starlette does NOT handle `If-None-Match`/304 for a plain route; the spine's poll contract silently assumes it does.**
Verified against Starlette `responses.py` (master): `FileResponse` **sets** an `ETag` header (md5 of `str(st_mtime)-str(st_size)`) but **never checks `If-None-Match` or `If-Modified-Since` and never returns 304** — conditional-request handling lives only in `StaticFiles.is_not_modified()`, which the HUD's dynamic `/projection` route won't go through. AD-6's "the page polls every 2–5s with `If-None-Match` and re-renders only on 200" therefore requires the route to implement the compare-and-304 itself, or the churn-prevention rationale of the AD is dead (every poll returns a full 200 body). This is exactly a training-data-plausible assertion that reality contradicts. **Fix:** one sentence in AD-6: "`/projection` implements the `If-None-Match` comparison itself and returns 304 with the ETag header — Starlette `FileResponse` sets ETag but does not do conditional 304s (verified 2026-07-11)." Cheap at dev time (~5 lines), expensive if discovered as a "why is the HUD re-rendering every 2s" bug.

**HIGH-3 — Memlog `(version)` record for Apprise is factually wrong; the Stack pin floor is ~3 minor versions stale.**
Memlog line 19 states "Verified current 2026-07-11: Apprise v1.9.8 (2026-07-04)". PyPI shows **1.9.8 released 2026-03-08** and the **current release is 1.12.0, released 2026-07-04** — the web check evidently captured the latest release *date* but attached it to the wrong version. Functional risk is low (`>=1.9.8,<2` resolves to 1.12.0; `pover://`/`ntfy://` URL syntaxes verified current at HEAD of the wiki), but the memlog `(version)` entry is precisely the audit line future stories will trust, and it is false. **Fix:** correct memlog line 19 (and the line-18 parenthetical "Apprise v1.9.8 (active, released 2026-07-04)"); consider floor bump to `>=1.12,<2` at dev, or leave floor and record "pin floor 1.9.8 (Mar 2026), latest 1.12.0 verified 2026-07-11".

### Medium

**MEDIUM-1 — ETag construction underspecified for a hand-rolled validator (consequence of HIGH-2).**
Since the route must build and compare the ETag itself (HIGH-2), AD-6's "ETag derived from mtime+size" should pin the recipe: a *quoted* strong validator (Starlette's own recipe — md5 of `mtime-size` — is a fine template), and note the free upgrade available here: the projection already carries a monotonic `seq` (AD-10), which is a strictly stronger and cheaper change-detector than mtime+size (immune to same-size same-timestamp-precision writes and to mtime quirks across the temp-file replace). Not blocking; pin at story level.

### Low

**LOW-1 — jsonschema listed as "already dep" `>=4`.** It is present only in the `dev` optional extra, pinned `>=4.0,<5`. Correct for its stated use (parity tests run under dev extras), but the Stack row should say `>=4,<5 (dev extra)` so nobody imports it from runtime code (`app/notify/`, `app/hud/`) expecting it installed in a bare prod env.

**LOW-2 — Stack table's requests annotation "(already dep; Pushover POST)" contradicts AD-9.** AD-9 mandates push goes through Apprise URL strings "so mechanism swap is config, not code"; a direct Pushover POST via requests is exactly the bypass that mandate forbids. requests stays a legitimate dep regardless (Apprise itself rides it). Reword the annotation to "(already dep; Apprise transport)" or drop the parenthetical.

---

## 3. What was checked and found sound (no action)

- All repo-pin Stack rows byte-match `pyproject.toml` (Python, pydantic, fastapi, uvicorn, requests).
- Pushover: exists, API stable, priority −2..2 maps to Apprise low→emergency, and the memlog's May-2026 per-account 10k-message pooling claim re-verified accurate against blog.pushover.net.
- ntfy: exists, actively integrated in Apprise; hosted `ntfy.sh` topic-URL form current.
- Apprise Pushover (`pover://user@token`) and ntfy (`ntfy://topic`, `ntfys://…`) URL string formats current at wiki HEAD — AD-9's config-not-code swap claim holds.
- `[ASSUMPTION]` hygiene is genuinely good: port, stall budget, Apprise-as-new-dep, `trial hud` CLI are all tagged and deferred to story/operator level rather than smuggled in as facts.
- Brownfield reality-checks (choke-point at `production_runner.py:221`, the ~3501 bypass, import-linter `app.gates` scheduler fence, shape-pin precedents, xdist marker exclusions) are backed by recorded sweep entries, not asserted.

## 4. Sources

- https://pypi.org/project/apprise/#history (1.12.0 → 2026-07-04; 1.9.8 → 2026-03-08)
- https://raw.githubusercontent.com/encode/starlette/master/starlette/responses.py (FileResponse ETag set, no 304 logic)
- https://github.com/caronc/apprise/wiki/Notify_pushover
- https://github.com/caronc/apprise/wiki/Notify_ntfy
- https://blog.pushover.net/posts/2026/4/app-limits (per-account pooling effective 2026-05-01)
- https://github.com/untitaker/python-atomicwrites/issues/25 (os.replace as the Windows atomic primitive)
- https://github.com/golang/go/issues/8914 (MoveFileEx atomic-replace semantics discussion)
- https://thelinuxcode.com/python-osrename-how-to-rename-files-and-directories-safely-atomic-moves-cross-device-pitfalls-and-production-patterns/ (Windows PermissionError with open handles; temp+replace reader guarantees)
- Repo: `pyproject.toml`, `.memlog.md` entries 18–24 (sweep + version records)
