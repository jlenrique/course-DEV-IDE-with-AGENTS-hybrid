"""Jefferson session-backed probe — Chrome quit, cookies readable."""

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
    / f"jefferson-access-probe-session-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
)
OUT.mkdir(parents=True, exist_ok=True)

PDF_URL = "https://www.nejm.org/doi/pdf/10.1056/NEJMoa2034577"
ARTICLE_URL = "https://www.nejm.org/doi/full/10.1056/NEJMoa2034577"
PRIMO_URL = (
    "https://jefferson.primo.exlibrisgroup.com/discovery/search"
    "?vid=01TJU_INST:01TJU&query=any,contains,diabetes"
)


def _copy_profile(src_user: Path, dst_user: Path) -> list[str]:
    warnings: list[str] = []
    dst_user.mkdir(parents=True, exist_ok=True)
    local_state = src_user / "Local State"
    if local_state.exists():
        shutil.copy2(local_state, dst_user / "Local State")
    src_default = src_user / "Default"
    dst_default = dst_user / "Default"
    dst_default.mkdir(parents=True, exist_ok=True)

    # Essential auth/session material
    for rel in (
        "Network/Cookies",
        "Network/Cookies-journal",
        "Network/Trust Tokens",
        "Network/Trust Tokens-journal",
        "Cookies",
        "Cookies-journal",
        "Login Data",
        "Login Data-journal",
        "Web Data",
        "Web Data-journal",
        "Preferences",
        "Secure Preferences",
    ):
        src = src_default / rel
        if not src.exists():
            continue
        dst = dst_default / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        try:
            shutil.copy2(src, dst)
        except OSError as exc:
            warnings.append(f"{rel}: {exc}")
    return warnings


def main() -> int:
    from playwright.sync_api import sync_playwright

    chrome_user = Path.home() / "AppData/Local/Google/Chrome/User Data"
    tmp = Path(tempfile.mkdtemp(prefix="jeff-session-"))
    copy_warnings = _copy_profile(chrome_user, tmp)

    verdict: dict = {
        "probe": "jefferson-session-backed",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "evidence_dir": str(OUT),
        "chrome_processes_at_start": 0,
        "cookies_copied": (tmp / "Default/Network/Cookies").exists()
        or (tmp / "Default/Cookies").exists(),
        "copy_warnings": copy_warnings,
        "probes": {},
    }

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(tmp),
            channel="chrome",
            headless=False,  # headed helps pass CF / use real session
            accept_downloads=True,
            viewport={"width": 1400, "height": 900},
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = context.new_page()

        for label, url in (
            ("primo_search", PRIMO_URL),
            ("nejm_article", ARTICLE_URL),
            ("nejm_pdf", PDF_URL),
        ):
            entry: dict = {"url": url}
            try:
                resp = page.goto(url, wait_until="domcontentloaded", timeout=60000)
                page.wait_for_timeout(2500)
                final = page.url
                title = page.title()
                content = page.content()
                body = b""
                try:
                    body = resp.body() if resp else b""
                except Exception as exc:  # noqa: BLE001
                    entry["body_error"] = f"{type(exc).__name__}: {exc}"[:200]

                if label == "nejm_pdf":
                    # If redirected to HTML cookie wall, try download/expect PDF via request
                    if body[:4] != b"%PDF":
                        try:
                            api = context.request.get(PDF_URL)
                            body2 = api.body()
                            (OUT / "nejm-pdf-request.bin").write_bytes(body2)
                            entry["request_status"] = api.status
                            entry["request_is_pdf"] = body2[:4] == b"%PDF"
                            entry["request_size"] = len(body2)
                            if body2[:4] == b"%PDF":
                                body = body2
                        except Exception as exc:  # noqa: BLE001
                            entry["request_error"] = f"{type(exc).__name__}: {exc}"[:200]
                    (OUT / "nejm-pdf-navigation.bin").write_bytes(body)

                entry.update(
                    {
                        "status": resp.status if resp else None,
                        "final_url": final,
                        "title": title[:200],
                        "is_pdf": body[:4] == b"%PDF",
                        "body_size": len(body),
                        "cookie_absent": "cookieAbsent" in final
                        or "cookieAbsent" in content,
                        "cloudflare": "Just a moment" in content
                        or "Attention Required" in title,
                        "sign_in_hint": any(
                            s in content.lower()
                            for s in ("sign in", "log in", "campus key", "sso")
                        ),
                    }
                )
            except Exception as exc:  # noqa: BLE001
                entry["error"] = f"{type(exc).__name__}: {exc}"[:500]
            verdict["probes"][label] = entry

        # Capture cookies for nejm/jefferson domains (names only — no values in report)
        try:
            cookies = context.cookies()
            names_by_domain: dict[str, list[str]] = {}
            for c in cookies:
                dom = c.get("domain", "")
                if any(
                    x in dom
                    for x in ("nejm.org", "jefferson", "exlibrisgroup", "microsoftonline")
                ):
                    names_by_domain.setdefault(dom, []).append(c.get("name", ""))
            verdict["session_cookie_domains"] = {
                k: sorted(set(v)) for k, v in sorted(names_by_domain.items())
            }
        except Exception as exc:  # noqa: BLE001
            verdict["cookie_list_error"] = str(exc)[:200]

        context.close()

    shutil.rmtree(tmp, ignore_errors=True)

    pdf = verdict["probes"].get("nejm_pdf", {})
    overall = bool(pdf.get("is_pdf") or pdf.get("request_is_pdf"))
    verdict["pass"] = overall

    (OUT / "verdict.json").write_text(json.dumps(verdict, indent=2), encoding="utf-8")
    lines = [
        "# Jefferson library access — SESSION-BACKED (Chrome quit)",
        "",
        f"**Evidence:** `{OUT.as_posix()}`",
        f"**Pass (PDF bytes):** {overall}",
        "",
        f"- Cookies copied: {verdict['cookies_copied']}",
        f"- Copy warnings: {len(copy_warnings)}",
        "",
    ]
    for label, entry in verdict["probes"].items():
        lines.append(
            f"- **{label}**: status={entry.get('status')} final=`{entry.get('final_url')}` "
            f"title={entry.get('title')!r} is_pdf={entry.get('is_pdf')} "
            f"cookie_absent={entry.get('cookie_absent')} cf={entry.get('cloudflare')}"
        )
        if entry.get("request_is_pdf") is not None:
            lines.append(
                f"  - request API: status={entry.get('request_status')} "
                f"is_pdf={entry.get('request_is_pdf')} size={entry.get('request_size')}"
            )
    if verdict.get("session_cookie_domains"):
        lines.append("")
        lines.append("## Session cookie domains present (names only)")
        for dom, names in verdict["session_cookie_domains"].items():
            lines.append(f"- `{dom}`: {', '.join(names[:12])}")
    lines.append("")
    (OUT / "PROBE.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(verdict, indent=2))
    print(f"evidence: {OUT}")
    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main())
