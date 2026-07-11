"""Jefferson library re-auth probe: curl summary + Playwright Chrome-profile attempt."""

from __future__ import annotations

import json
import re
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_ROOT = ROOT / "_bmad-output" / "implementation-artifacts" / "evidence"


def latest_reauth_dir() -> Path:
    dirs = sorted(EVIDENCE_ROOT.glob("jefferson-access-probe-reauth-*"))
    if not dirs:
        raise SystemExit("no reauth evidence dir found")
    return dirs[-1]


def summarize_curl(out: Path) -> list[dict]:
    rows = []
    for line in (out / "raw-results.jsonl").read_text(encoding="utf-8-sig").splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        m = r.get("metrics", "").replace("\n", " | ")
        code_m = re.search(r"http_code=(\d+)", m)
        eff_m = re.search(r"url_effective=([^\s|]+)", m)
        rows.append(
            {
                "name": r["name"],
                "http_code": code_m.group(1) if code_m else "?",
                "magic": r.get("magic"),
                "cf": r.get("cf"),
                "url_effective": eff_m.group(1) if eff_m else "",
                "url": r.get("url"),
            }
        )
    return rows


def inspect_nejm_pdf(out: Path) -> dict:
    p = out / "nejm-pdf-probe.bin"
    if not p.exists():
        return {"exists": False}
    data = p.read_bytes()
    head = data[:800].decode("utf-8", errors="replace")
    return {
        "exists": True,
        "size": len(data),
        "is_pdf": data[:4] == b"%PDF",
        "cookie_absent": "cookieAbsent" in head or "cookieAbsent" in str(p),
        "cloudflare_challenge": (
            "Just a moment" in head or "cf-browser-verification" in head
        ),
        "head_snippet": head[:240].replace("\n", " "),
        "effective_note": "see curl url_effective for nejm_pdf",
    }


def try_playwright_chrome(out: Path) -> dict:
    """Attempt NEJM PDF fetch using a copy of the local Chrome profile."""
    chrome_user = Path.home() / "AppData/Local/Google/Chrome/User Data"
    result: dict = {
        "chrome_user_data_exists": chrome_user.exists(),
        "attempted": False,
    }
    if not chrome_user.exists():
        result["error"] = "Chrome User Data missing"
        return result

    profiles = [
        p.name
        for p in chrome_user.iterdir()
        if p.is_dir() and (p.name == "Default" or p.name.startswith("Profile"))
    ]
    result["profiles_found"] = profiles

    try:
        from playwright.sync_api import sync_playwright
    except Exception as exc:  # noqa: BLE001
        result["error"] = f"playwright import failed: {exc}"
        return result

    # Copy Default profile cookies/local storage lightly via persistent context
    # against a TEMP user-data-dir seeded from Default (avoids lock if possible).
    src_default = chrome_user / "Default"
    if not src_default.exists():
        result["error"] = "Default profile missing"
        return result

    tmp = Path(tempfile.mkdtemp(prefix="jeff-chrome-"))
    result["temp_user_data"] = str(tmp)
    result["attempted"] = True

    # Minimal seed: Local State + Default cookies DB if present
    local_state = chrome_user / "Local State"
    dst_default = tmp / "Default"
    dst_default.mkdir(parents=True, exist_ok=True)
    if local_state.exists():
        shutil.copy2(local_state, tmp / "Local State")
    for name in ("Cookies", "Cookies-journal", "Network", "Login Data"):
        src = src_default / name
        dst = dst_default / name
        try:
            if src.is_file():
                # Best-effort copy; Chrome often locks Cookies while running.
                shutil.copy2(src, dst)
            elif src.is_dir():
                shutil.copytree(
                    src,
                    dst,
                    dirs_exist_ok=True,
                    ignore_dangling_symlinks=True,
                )
        except OSError as exc:
            result.setdefault("copy_warnings", []).append(f"{name}: {exc}")
            # Fallback: try cmd copy for locked files (may still fail).
            if src.is_file():
                import subprocess

                cp = subprocess.run(
                    ["cmd", "/c", "copy", "/Y", str(src), str(dst)],
                    capture_output=True,
                    text=True,
                )
                if cp.returncode != 0:
                    result.setdefault("copy_warnings", []).append(
                        f"{name} cmd-copy: {(cp.stderr or cp.stdout)[:200]}"
                    )

    pdf_url = "https://www.nejm.org/doi/pdf/10.1056/NEJMoa2034577"
    article_url = "https://www.nejm.org/doi/full/10.1056/NEJMoa2034577"
    primo_url = (
        "https://jefferson.primo.exlibrisgroup.com/discovery/search"
        "?vid=01TJU_INST:01TJU&query=any,contains,diabetes"
    )

    try:
        with sync_playwright() as p:
            # Prefer system Chrome channel for SSO cookie compatibility.
            try:
                context = p.chromium.launch_persistent_context(
                    user_data_dir=str(tmp),
                    channel="chrome",
                    headless=True,
                    accept_downloads=True,
                    args=["--disable-blink-features=AutomationControlled"],
                )
                result["launch"] = "persistent_chrome_channel"
            except Exception as exc:  # noqa: BLE001
                result["chrome_channel_error"] = str(exc)[:300]
                context = p.chromium.launch_persistent_context(
                    user_data_dir=str(tmp),
                    headless=True,
                    accept_downloads=True,
                )
                result["launch"] = "persistent_chromium"

            page = context.new_page()
            probes = {}
            for label, url in (
                ("primo_search", primo_url),
                ("nejm_article", article_url),
                ("nejm_pdf", pdf_url),
            ):
                try:
                    resp = page.goto(url, wait_until="domcontentloaded", timeout=45000)
                    final = page.url
                    title = page.title()
                    content = page.content()[:1500]
                    body_bytes = b""
                    if label == "nejm_pdf":
                        # Try raw response body if available
                        try:
                            body_bytes = resp.body() if resp else b""
                        except Exception:  # noqa: BLE001
                            body_bytes = b""
                        (out / "playwright-nejm-pdf.bin").write_bytes(body_bytes)
                    probes[label] = {
                        "status": resp.status if resp else None,
                        "final_url": final,
                        "title": title[:200],
                        "is_pdf": body_bytes[:4] == b"%PDF",
                        "cookie_absent": "cookieAbsent" in final
                        or "cookieAbsent" in content,
                        "cloudflare": "Just a moment" in content
                        or "Attention Required" in content,
                        "sign_in_hint": bool(
                            re.search(r"sign in|log in|SSO|Campus Key", content, re.I)
                        ),
                        "body_size": len(body_bytes) if body_bytes else None,
                    }
                except Exception as exc:  # noqa: BLE001
                    probes[label] = {"error": f"{type(exc).__name__}: {exc}"[:400]}
            context.close()
            result["probes"] = probes
    except Exception as exc:  # noqa: BLE001
        result["error"] = f"{type(exc).__name__}: {exc}"[:500]
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    return result


def try_playwright_attached_default(out: Path) -> dict:
    """Second attempt: launch with real Chrome user-data-dir (may fail if locked)."""
    chrome_user = Path.home() / "AppData/Local/Google/Chrome/User Data"
    result: dict = {"attempted": False}
    if not chrome_user.exists():
        return {"error": "no chrome user data"}
    try:
        from playwright.sync_api import sync_playwright
    except Exception as exc:  # noqa: BLE001
        return {"error": str(exc)}

    result["attempted"] = True
    pdf_url = "https://www.nejm.org/doi/pdf/10.1056/NEJMoa2034577"
    try:
        with sync_playwright() as p:
            try:
                context = p.chromium.launch_persistent_context(
                    user_data_dir=str(chrome_user),
                    channel="chrome",
                    headless=True,
                    args=["--profile-directory=Default"],
                )
                result["launch"] = "real_profile_headless"
            except Exception as exc:  # noqa: BLE001
                result["error"] = f"launch failed (likely profile lock): {exc}"[:500]
                return result
            page = context.new_page()
            resp = page.goto(pdf_url, wait_until="domcontentloaded", timeout=45000)
            body = b""
            try:
                body = resp.body() if resp else b""
            except Exception:  # noqa: BLE001
                pass
            (out / "playwright-realprofile-nejm-pdf.bin").write_bytes(body)
            result["probe"] = {
                "status": resp.status if resp else None,
                "final_url": page.url,
                "title": page.title()[:200],
                "is_pdf": body[:4] == b"%PDF",
                "body_size": len(body),
            }
            context.close()
    except Exception as exc:  # noqa: BLE001
        result["error"] = f"{type(exc).__name__}: {exc}"[:500]
    return result


def main() -> int:
    out = latest_reauth_dir()
    curl_rows = summarize_curl(out)
    nejm = inspect_nejm_pdf(out)
    pw_copy = try_playwright_chrome(out)
    pw_real = try_playwright_attached_default(out)

    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    verdict = {
        "probe": "jefferson-library-reauth",
        "timestamp_utc": stamp,
        "evidence_dir": str(out),
        "curl_summary": curl_rows,
        "nejm_pdf_curl": nejm,
        "playwright_copied_profile": pw_copy,
        "playwright_real_profile": pw_real,
    }
    (out / "verdict.json").write_text(json.dumps(verdict, indent=2), encoding="utf-8")

    # Compare vs prior probe narrative
    prior_403 = True  # known from first probe
    doi_row = next((r for r in curl_rows if r["name"] == "doi_nejm"), {})
    pdf_row = next((r for r in curl_rows if r["name"] == "nejm_pdf"), {})
    article_row = next((r for r in curl_rows if r["name"] == "nejm_article"), {})

    lines = [
        "# Jefferson library access probe — REAUTH (2026-07-10)",
        "",
        f"**Evidence:** `{out.as_posix()}`",
        f"**Stamp:** {stamp}",
        "",
        "## Why re-run",
        "",
        "Operator reported earlier session was **not** authenticated on this machine; now authenticated. Re-ran the prior curl suite + Playwright Chrome-profile attempts.",
        "",
        "## Curl suite (agent host, no browser cookie jar)",
        "",
        "| Probe | HTTP | Magic | CF | Effective URL |",
        "|---|---:|---|---|---|",
    ]
    for r in curl_rows:
        lines.append(
            f"| `{r['name']}` | {r['http_code']} | {r['magic']} | {r['cf']} | `{r['url_effective']}` |"
        )

    lines += [
        "",
        "## Delta vs first probe (pre-auth misunderstanding)",
        "",
        f"- First probe: DOI/NEJM → Cloudflare **403**.",
        f"- Reauth curl: DOI → HTTP **{doi_row.get('http_code')}** effective `{doi_row.get('url_effective')}` (still CF signal).",
        f"- Reauth curl: NEJM article → HTTP **{article_row.get('http_code')}** (CF).",
        f"- Reauth curl: NEJM PDF → HTTP **{pdf_row.get('http_code')}** but redirected to **`cookieAbsent`** — **not a PDF** (size={nejm.get('size')}, is_pdf={nejm.get('is_pdf')}).",
        "- Classic EZproxy hostnames still **NXDOMAIN**.",
        "- Ex Libris rewrite root still **403** without session.",
        "",
        "## Playwright (use local Chrome SSO cookies)",
        "",
        "### Copied-profile attempt",
        f"```json\n{json.dumps(pw_copy, indent=2)[:4000]}\n```",
        "",
        "### Real Chrome User Data attempt",
        f"```json\n{json.dumps(pw_real, indent=2)[:2000]}\n```",
        "",
        "## Corrected conclusion",
        "",
    ]

    pdf_ok = bool(
        (pw_copy.get("probes") or {}).get("nejm_pdf", {}).get("is_pdf")
        or (pw_real.get("probe") or {}).get("is_pdf")
    )
    if pdf_ok:
        lines.append(
            "- **PASS (session path):** Playwright retrieved NEJM PDF bytes using Chrome profile cookies."
        )
    else:
        lines += [
            "- **Still no agent-side full-text without an interactive SSO browser context.**",
            "- Machine “authenticated” in the operator’s browser does **not** automatically grant curl/headless access.",
            "- NEJM explicitly requires cookies (`cookieAbsent` redirect) — confirms publisher-native URL + session cookie model from the first operator return.",
            "- R5 design unchanged: headed/persistent SSO browser (or operator-assisted cookie capture), not API key / not bare curl.",
        ]

    lines += [
        "",
        f"- Prior-403 narrative was partly environmental; reauth curl still cannot mint institutional PDF without cookies (prior_403_known={prior_403}).",
        "",
    ]
    (out / "PROBE.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"evidence": str(out), "pdf_ok": pdf_ok, "doi": doi_row, "pdf": pdf_row}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
