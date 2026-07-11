"""Jefferson session probe v2 — OpenURL first, then wait out Cloudflare."""

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
    / f"jefferson-access-probe-session2-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
)
OUT.mkdir(parents=True, exist_ok=True)

OPENURL = (
    "https://jefferson.primo.exlibrisgroup.com/discovery/openurl"
    "?vid=01TJU_INST:01TJU&url_ver=Z39.88-2004"
    "&rft_id=info:doi/10.1056/NEJMoa2034577"
)
PDF_URL = "https://www.nejm.org/doi/pdf/10.1056/NEJMoa2034577"


def copy_profile(src_user: Path, dst_user: Path) -> None:
    dst_user.mkdir(parents=True, exist_ok=True)
    if (src_user / "Local State").exists():
        shutil.copy2(src_user / "Local State", dst_user / "Local State")
    src_default = src_user / "Default"
    dst_default = dst_user / "Default"
    dst_default.mkdir(parents=True, exist_ok=True)
    # Copy whole Network dir + Preferences for CF clearance cookies
    for rel in ("Network", "Preferences", "Secure Preferences", "Local Storage", "Session Storage"):
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

    chrome_user = Path.home() / "AppData/Local/Google/Chrome/User Data"
    tmp = Path(tempfile.mkdtemp(prefix="jeff-session2-"))
    copy_profile(chrome_user, tmp)

    verdict: dict = {
        "probe": "jefferson-session-v2-openurl-cfwait",
        "evidence_dir": str(OUT),
        "steps": [],
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
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-features=IsolateOrigins,site-per-process",
            ],
        )
        # Soften automation fingerprint
        page = context.new_page()
        page.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"
        )

        # Step 1: OpenURL via Jefferson discovery
        page.goto(OPENURL, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(5000)
        verdict["steps"].append(
            {
                "step": "openurl",
                "final_url": page.url,
                "title": page.title()[:200],
                "content_len": len(page.content()),
            }
        )
        page.screenshot(path=str(OUT / "01-openurl.png"), full_page=True)

        # Click any obvious full-text / PDF / View it controls if present
        clicked = None
        for sel in (
            "text=PDF",
            "text=Full Text",
            "text=View it",
            "text=View Online",
            "text=Available Online",
            "a[href*='nejm.org']",
            "a[href*='doi.org']",
        ):
            loc = page.locator(sel).first
            try:
                if loc.count() and loc.is_visible(timeout=1500):
                    loc.click(timeout=3000)
                    page.wait_for_timeout(3000)
                    clicked = sel
                    break
            except Exception:
                continue
        verdict["steps"].append(
            {
                "step": "click_attempt",
                "clicked": clicked,
                "final_url": page.url,
                "title": page.title()[:200],
            }
        )
        page.screenshot(path=str(OUT / "02-after-click.png"), full_page=True)

        # Step 2: direct PDF with long CF wait
        page.goto(PDF_URL, wait_until="domcontentloaded", timeout=60000)
        # Wait up to ~45s for Cloudflare / cookie redirect to settle
        pdf_ok = False
        body = b""
        for i in range(15):
            page.wait_for_timeout(3000)
            title = page.title()
            final = page.url
            content = page.content()
            if "Just a moment" in title or "Just a moment" in content:
                verdict.setdefault("cf_waits", []).append(
                    {"i": i, "title": title, "url": final}
                )
                continue
            if "cookieAbsent" in final:
                break
            # Try fetch via page.evaluate to get arraybuffer
            try:
                result = page.evaluate(
                    """async (url) => {
                      const r = await fetch(url, {credentials: 'include'});
                      const buf = await r.arrayBuffer();
                      const bytes = Array.from(new Uint8Array(buf).slice(0, 8));
                      return {status: r.status, size: buf.byteLength, head: bytes, ct: r.headers.get('content-type')};
                    }""",
                    PDF_URL,
                )
                verdict["fetch_probe"] = result
                head = bytes(result.get("head") or [])
                if head.startswith(b"%PDF") or (
                    result.get("ct") or ""
                ).startswith("application/pdf"):
                    # pull full body
                    full = page.evaluate(
                        """async (url) => {
                          const r = await fetch(url, {credentials: 'include'});
                          const buf = await r.arrayBuffer();
                          return Array.from(new Uint8Array(buf));
                        }""",
                        PDF_URL,
                    )
                    body = bytes(full)
                    pdf_ok = body[:4] == b"%PDF"
                    break
            except Exception as exc:  # noqa: BLE001
                verdict.setdefault("fetch_errors", []).append(str(exc)[:200])
            # also check response from navigation
            break

        page.screenshot(path=str(OUT / "03-pdf.png"), full_page=True)
        if body:
            (OUT / "nejm.pdf").write_bytes(body)

        # Cookie domain inventory (names only)
        cookies = context.cookies()
        interesting = {}
        for c in cookies:
            dom = c.get("domain", "")
            name = c.get("name", "")
            if any(
                x in dom
                for x in (
                    "nejm",
                    "jefferson",
                    "exlibris",
                    "cloudflare",
                    "microsoft",
                    "okta",
                    "duosecurity",
                )
            ) or name.lower().startswith("cf_"):
                interesting.setdefault(dom, []).append(name)
        verdict["cookies"] = {k: sorted(set(v)) for k, v in sorted(interesting.items())}
        verdict["final_pdf_url"] = page.url
        verdict["final_title"] = page.title()[:200]
        verdict["pass"] = pdf_ok
        verdict["pdf_size"] = len(body)

        context.close()

    shutil.rmtree(tmp, ignore_errors=True)
    (OUT / "verdict.json").write_text(json.dumps(verdict, indent=2), encoding="utf-8")
    (OUT / "PROBE.md").write_text(
        "\n".join(
            [
                "# Jefferson session probe v2 (OpenURL + CF wait)",
                "",
                f"**Pass:** {pdf_ok}",
                f"**PDF size:** {len(body)}",
                f"**Final URL:** `{verdict.get('final_pdf_url')}`",
                f"**Title:** {verdict.get('final_title')!r}",
                "",
                "See verdict.json + screenshots.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(json.dumps(verdict, indent=2))
    print(f"evidence: {OUT}")
    return 0 if pdf_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
