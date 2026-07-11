#!/usr/bin/env python3
"""OpenAlex LIVE smoke — DOI metadata + OA link discovery (no PDF/SSO).

TRAIL trio slice 1. Claim fence: public OpenAlex Works API returns metadata
and open-access *URLs* only. Does not download PDFs or use institutional SSO.

Usage (repo root)::

    python scripts/utilities/run_openalex_live_evidence.py
"""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "skills" / "bmad-agent-texas" / "scripts"))

from retrieval.contracts import (  # noqa: E402
    AcceptanceCriteria,
    ProviderHint,
    RetrievalIntent,
)
from retrieval.openalex_provider import OpenAlexProvider  # noqa: E402
from retrieval.provider_directory import get_provider  # noqa: E402

# Well-known OA DOI (Nature / COVID vaccinations database) — public metadata.
LIVE_DOI = "10.1038/s41586-020-2649-2"
# Negative control: nonsense DOI should yield empty (or 404 → []).
NEGATIVE_DOI = "10.9999/this-doi-does-not-exist-openalex-trail-2026"


def _stamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")


def _case(provider: OpenAlexProvider, *, doi: str, case_id: str) -> dict:
    intent = RetrievalIntent(
        intent=doi,
        provider_hints=[ProviderHint(provider="openalex", params={"doi": doi})],
        kind="direct_ref",
        acceptance_criteria=AcceptanceCriteria(mechanical={"min_results": 1}),
    )
    query = provider.formulate_query(intent)
    try:
        raw = provider.execute(query)
        rows = provider.normalize(raw)
        error = None
    except Exception as exc:  # noqa: BLE001 — live witness captures transport
        raw = []
        rows = []
        error = f"{type(exc).__name__}: {exc}"
    return {
        "case_id": case_id,
        "doi": doi,
        "query": query,
        "error": error,
        "raw_count": len(raw),
        "row_count": len(rows),
        "rows": [
            {
                "source_id": r.source_id,
                "title": r.title,
                "provider": r.provider,
                "openalex": (r.provider_metadata or {}).get("openalex"),
            }
            for r in rows
        ],
    }


def main() -> int:
    info = get_provider("openalex")
    if info is None or info.status != "ready":
        print("FAIL: openalex not registered ready")
        return 2

    provider = OpenAlexProvider()  # live fetch_fn=None → public API
    positive = _case(provider, doi=LIVE_DOI, case_id="positive_oa_doi")
    negative = _case(provider, doi=NEGATIVE_DOI, case_id="negative_missing_doi")

    pos_ok = (
        positive["error"] is None
        and positive["row_count"] >= 1
        and positive["rows"][0]["openalex"] is not None
    )
    # Negative: empty rows OR transport error is acceptable; inventing a hit is not.
    neg_ok = negative["row_count"] == 0

    claim = {
        "claim": "DOI metadata + OA link discovery via OpenAlex public API",
        "non_claims": [
            "PDF byte download",
            "institutional SSO",
            "claim↔source semantic validation",
            "arbiter / credibility scoring",
        ],
        "provider_id": "openalex",
        "live_doi": LIVE_DOI,
    }
    overall = bool(pos_ok and neg_ok)
    pack = ROOT / "_bmad-output/implementation-artifacts/evidence" / f"openalex-live-{_stamp()}"
    pack.mkdir(parents=True, exist_ok=True)
    verdict = {
        "pass": overall,
        "positive_ok": pos_ok,
        "negative_ok": neg_ok,
        "claim": claim,
        "positive": positive,
        "negative": negative,
    }
    (pack / "verdict.json").write_text(
        json.dumps(verdict, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    proof_lines = [
        "# PROOF — OpenAlex LIVE smoke (TRAIL trio slice 1)",
        "",
        f"**pass={overall}** positive_ok={pos_ok} negative_ok={neg_ok}",
        "",
        f"- Claim: {claim['claim']}",
        f"- Non-claims: {', '.join(claim['non_claims'])}",
        f"- Positive DOI `{LIVE_DOI}` rows={positive['row_count']}",
        f"- Negative DOI `{NEGATIVE_DOI}` rows={negative['row_count']}",
        "",
    ]
    if positive["rows"]:
        oa = positive["rows"][0]["openalex"] or {}
        proof_lines.append(
            f"- OA: is_oa={oa.get('is_oa')} oa_status={oa.get('oa_status')} "
            f"oa_url_count={len(oa.get('oa_urls') or [])}"
        )
        proof_lines.append(f"- Title: {positive['rows'][0].get('title')}")
    (pack / "PROOF.md").write_text("\n".join(proof_lines) + "\n", encoding="utf-8")
    print(json.dumps({"pass": overall, "pack": str(pack)}, indent=2))
    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main())
