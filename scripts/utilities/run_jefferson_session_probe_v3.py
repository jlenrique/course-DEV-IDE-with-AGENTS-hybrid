"""Jefferson session probe v3 — capture real application/pdf network bytes."""

from __future__ import annotations

import json
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = (
    ROOT
    / "_bmad-output"
    / "implementation-artifacts"
    / "evidence"
    / f"jefferson-access-probe-session3-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
)
OUT.mkdir(parents=True, exist_ok=True)

PDF_URL = "https://www.nejm.org/doi/pdf/10.1056/NEJMoa2034577"
OPENURL = (
    "https://jefferson.primo.exlibrisgroup.com/discovery/openurl"
    "?vid=01TJU_INST:01TJU&url_ver=Z39.88-2004"
    "&rft_id=info:doi/10.1056/NEJMoa2034577"
)


def copy_profile(src_user: Path, dst_user: Path) -> None:
    dst_user.mkdir(parents=True, exist_ok=True)
    if (src_user / "Local State").exists():
        shutil.copy2(src_user / "Local State", dst_user / "Local State")
    src_default = src_user / "Default"
    dst_default = dst_user / "Default"
    dst_default.mkdir(parents=True, exist_ok=True)
    for rel in ("Network", "Preferences", "Secure Preferences"):
        src = src_default / rel
        if not src.exists():
            continue
        dst = dst_default / rel
        if src.is_dir():
            shutil.copytree(src, dst, dirs_exist_ok=True)
        else:
            shutil.copy2(src, dst)


def main() -> int:
    from playwright.sync_api import sync_playwright

    # Confirm Chrome still quit
    import subprocess

    chrome = subprocess.run(
        ["powershell", "-NoProfile", "-Command", "(Get-Process chrome -ErrorAction SilentlyContinue).Count"],
        capture_output=True,
        text=True,
    )
    chrome_count = (chrome.stdout or "").strip() or "unknown"

    chrome_user = Path.home() / "AppData/Local/Google/Chrome/User Data"
    tmp = Path(tempfile.mkdtemp(prefix="jeff-session3-"))
    copy_profile(chrome_user, tmp)

    pdf_hits: list[dict] = []
    verdict: dict = {
        "probe": "jefferson-session-v3-pdf-network",
        "chrome_count": chrome_count,
        "evidence_dir": str(OUT),
        "pass": False,
    }

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(tmp),
            channel="chrome",
            headless=False,
            accept_downloads=True,
            viewport={"width": 1400, "height": 900},
            ignore_default_args=["--enable-automation"],
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = context.new_page()
        page.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"
        )

        def on_response(resp) -> None:  # noqa: ANN001
            try:
                ct = (resp.headers.get("content-type") or "").lower()
                url = resp.url
                if "pdf" in ct or url.lower().endswith(".pdf") or "/doi/pdf/" in url:
                    item = {
                        "url": url,
                        "status": resp.status,
                        "content_type": ct,
                    }
                    try:
                        body = resp.body()
                        item["size"] = len(body)
                        item["is_pdf"] = body[:4] == b"%PDF"
                        if item["is_pdf"]:
                            dest = OUT / f"captured-{len(pdf_hits)}.pdf"
                            dest.write_bytes(body)
                            item["saved"] = str(dest)
                    except Exception as exc:  # noqa: BLE001
                        item["body_error"] = f"{type(exc).__name__}: {exc}"[:200]
                    pdf_hits.append(item)
            except Exception:
                pass

        page.on("response", on_response)

        # Warm via OpenURL
        page.goto(OPENURL, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(4000)
        verdict["openurl_final"] = page.url
        verdict["openurl_title"] = page.title()[:200]
        page.screenshot(path=str(OUT / "01-openurl.png"))

        # Direct PDF navigation — listen for application/pdf
        page.goto(PDF_URL, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(8000)
        verdict["pdf_nav_final"] = page.url
        verdict["pdf_nav_title"] = page.title()[:200]
        page.screenshot(path=str(OUT / "02-pdf-nav.png"))

        # API request with browser cookies (bypasses PDF viewer shell)
        api = context.request.get(PDF_URL)
        api_body = api.body()
        (OUT / "api-request.bin").write_bytes(api_body)
        verdict["api_request"] = {
            "status": api.status,
            "content_type": api.headers.get("content-type"),
            "size": len(api_body),
            "is_pdf": api_body[:4] == b"%PDF",
            "head_ascii": api_body[:120].decode("latin-1", errors="replace"),
        }
        if api_body[:4] == b"%PDF":
            (OUT / "nejm-api.pdf").write_bytes(api_body)

        # In-page fetch
        try:
            fetch_meta = page.evaluate(
                """async (url) => {
                  const r = await fetch(url, {credentials:'include'});
                  const buf = await r.arrayBuffer();
                  const u8 = new Uint8Array(buf);
                  const head = Array.from(u8.slice(0, 8));
                  return {
                    status: r.status,
                    size: u8.length,
                    contentType: r.headers.get('content-type'),
                    head,
                    isPdf: u8[0]===0x25 && u8[1]===0x50 && u8[2]===0x44 && u8[3]===0x46
                  };
                }""",
                PDF_URL,
            )
            verdict["page_fetch"] = fetch_meta
            if fetch_meta.get("isPdf"):
                full = page.evaluate(
                    """async (url) => {
                      const r = await fetch(url, {credentials:'include'});
                      const buf = await r.arrayBuffer();
                      return Array.from(new Uint8Array(buf));
                    }""",
                    PDF_URL,
                )
                pdf_bytes = bytes(full)
                (OUT / "nejm-page-fetch.pdf").write_bytes(pdf_bytes)
                verdict["page_fetch"]["saved"] = str(OUT / "nejm-page-fetch.pdf")
        except Exception as exc:  # noqa: BLE001
            verdict["page_fetch_error"] = f"{type(exc).__name__}: {exc}"[:300]

        verdict["pdf_network_hits"] = pdf_hits
        verdict["pass"] = bool(
            verdict["api_request"].get("is_pdf")
            or (verdict.get("page_fetch") or {}).get("isPdf")
            or any(h.get("is_pdf") for h in pdf_hits)
        )

        # cookie names
        cookies = context.cookies()
        interesting = {}
        for c in cookies:
            dom = c.get("domain", "")
            name = c.get("name", "")
            if any(x in dom for x in ("nejm", "jefferson", "exlibris", "cloudflare")) or name.lower().startswith("cf_"):
                interesting.setdefault(dom, []).append(name)
        verdict["cookies"] = {k: sorted(set(v)) for k, v in sorted(interesting.items())}

        context.close()

    shutil.rmtree(tmp, ignore_errors=True)
    (OUT / "verdict.json").write_text(json.dumps(verdict, indent=2), encoding="utf-8")
    (OUT / "PROBE.md").write_text(
        "\n".join(
            [
                "# Jefferson session probe v3 — PDF network capture",
                "",
                f"**Pass:** {verdict['pass']}",
                f"**Chrome count at start:** {chrome_count}",
                f"**API request PDF:** {verdict['api_request']}",
                f"**Page fetch:** {verdict.get('page_fetch')}",
                f"**Network PDF hits:** {len(pdf_hits)}",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(json.dumps(verdict, indent=2))
    print(f"evidence: {OUT}")
    return 0 if verdict["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
