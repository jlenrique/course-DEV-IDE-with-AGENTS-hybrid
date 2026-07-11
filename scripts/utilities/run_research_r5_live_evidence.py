#!/usr/bin/env python3
"""R5 live evidence — Jefferson library full-text (or creds/session fence).

Arms ``JEFFERSON_LIBRARY_LIVE=1`` and attempts the browser-session PDF fetch
for a known DOI. If Chrome is running, profile missing, or SSO cookies fail,
writes an explicit fence — does not fake live.

Usage::

    # Quit Chrome first (cookie DB must be readable), then:
    python scripts/utilities/run_research_r5_live_evidence.py
"""

from __future__ import annotations

import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "skills" / "bmad-agent-texas" / "scripts"))

DOI = "10.1056/NEJMoa2034577"
PDF_URL = f"https://www.nejm.org/doi/pdf/{DOI}"


def _stamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")


def main() -> int:
    from retrieval.contracts import AcceptanceCriteria, ProviderHint, RetrievalIntent
    from retrieval.dispatcher import dispatch
    from retrieval.jefferson_library_provider import (
        JEFFERSON_ALLOW_LIVE_ENV,
        JeffersonLibraryAuthError,
        JeffersonLibraryFetchError,
        jefferson_session_preflight,
    )

    os.environ[JEFFERSON_ALLOW_LIVE_ENV] = "1"

    out_dir = (
        ROOT
        / "_bmad-output"
        / "implementation-artifacts"
        / "evidence"
        / f"research-r5-{_stamp()}"
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    preflight = jefferson_session_preflight()
    (out_dir / "preflight.json").write_text(
        json.dumps(preflight, indent=2), encoding="utf-8"
    )

    if not preflight.get("ready"):
        reason = []
        if not preflight.get("chrome_user_data_exists"):
            reason.append("chrome_user_data_missing")
        if preflight.get("cookies_likely_locked"):
            reason.append("chrome_running_quit_required")
        if not preflight.get("live_armed"):
            reason.append("live_not_armed")
        verdict = {
            "story": "research-r5",
            "pass": False,
            "fence": "jefferson-session-absent-or-locked",
            "reasons": reason or ["preflight_not_ready"],
            "preflight": preflight,
            "note": (
                "Do not fake live. Quit Chrome after SSO login, re-run this script, "
                "or accept fence until operator session is available."
            ),
        }
        (out_dir / "verdict.json").write_text(
            json.dumps(verdict, indent=2), encoding="utf-8"
        )
        (out_dir / "PROOF.md").write_text(
            "\n".join(
                [
                    "# PROOF R5 — Jefferson library FENCED",
                    "",
                    f"reasons: {', '.join(verdict['reasons'])}",
                    "",
                    verdict["note"],
                    "",
                ]
            ),
            encoding="utf-8",
        )
        print(json.dumps(verdict, indent=2))
        print(f"evidence: {out_dir}")
        # Exit 0 on honest fence — AC allows documented fence when session absent.
        return 0

    intent = RetrievalIntent(
        intent=DOI,
        provider_hints=[
            ProviderHint(
                provider="jefferson_library",
                params={"doi": DOI, "pdf_url": PDF_URL, "title": "NEJM live R5"},
            )
        ],
        kind="direct_ref",
        convergence_required=False,
        cross_validate=False,
        acceptance_criteria=AcceptanceCriteria(mechanical={"min_results": 1}),
    )

    error = None
    summary: dict = {}
    try:
        result = dispatch(intent)
        results = result if isinstance(result, list) else [result]
        rows = []
        for pr in results:
            for row in getattr(pr, "rows", []) or []:
                meta = (row.provider_metadata or {}).get("jefferson_library") or {}
                rows.append(
                    {
                        "provider": row.provider,
                        "source_id": row.source_id,
                        "title": row.title,
                        "is_pdf": meta.get("is_pdf"),
                        "pdf_bytes_len": meta.get("pdf_bytes_len"),
                        "pdf_sha256": meta.get("pdf_sha256"),
                        "access_path": meta.get("access_path"),
                    }
                )
        summary = {
            "provider_result_count": len(results),
            "row_count": len(rows),
            "rows": rows,
            "acceptance_met": all(getattr(pr, "acceptance_met", False) for pr in results),
        }
    except (JeffersonLibraryAuthError, JeffersonLibraryFetchError) as exc:
        error = f"{type(exc).__name__}: {exc}"
    except Exception as exc:  # noqa: BLE001
        error = f"{type(exc).__name__}: {exc}"

    live_ok = (
        error is None
        and summary.get("row_count", 0) >= 1
        and any(r.get("is_pdf") for r in summary.get("rows") or [])
    )
    verdict = {
        "story": "research-r5",
        "doi": DOI,
        "preflight": preflight,
        "summary": summary,
        "error": error,
        "pass": live_ok,
        "fence": None if live_ok else ("fetch-failed" if error else "no-pdf-row"),
    }
    (out_dir / "verdict.json").write_text(json.dumps(verdict, indent=2), encoding="utf-8")
    lines = [
        "# PROOF R5 — Jefferson library live",
        "",
        f"pass={live_ok}",
        f"doi={DOI}",
        "",
    ]
    if error:
        lines.append(f"error: `{error}`")
    for row in summary.get("rows") or []:
        lines.append(
            f"- `{row.get('source_id')}` pdf={row.get('is_pdf')} "
            f"bytes={row.get('pdf_bytes_len')} path={row.get('access_path')}"
        )
    lines.append("")
    (out_dir / "PROOF.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(verdict, indent=2))
    print(f"evidence: {out_dir}")
    return 0 if live_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
