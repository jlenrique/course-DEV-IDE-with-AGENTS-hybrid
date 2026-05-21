"""5-API live-binding smoke (AC-I; operator-gated; spend-ceilinged).

Default mode fails closed with structured ``not_run`` JSON. ``--live`` loads
the operator's ``.env`` and invokes post-Slab-7c API clients through safe
read/connectivity probes for Gamma, ElevenLabs, Canvas, Qualtrics, and Panopto.
Missing credentials skip individual APIs; no mutating canaries run here.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.api_clients.base_client import APIError  # noqa: E402
from scripts.utilities.env_loader import load_env  # noqa: E402

DEFAULT_APIS: tuple[str, ...] = (
    "gamma",
    "elevenlabs",
    "canvas",
    "qualtrics",
    "panopto",
)
PLACEHOLDER_PREFIXES = ("placeholder", "sk-substrate-no-real-key-do-not-invoke")


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="AC-I 5-API live-binding smoke (operator-gated; cost <=$6.00).",
    )
    parser.add_argument(
        "--apis",
        default=",".join(DEFAULT_APIS),
        help="Comma-separated API names to smoke",
    )
    parser.add_argument(
        "--max-canaries-per-api",
        type=int,
        default=3,
        help="Max canary calls per API (default 3)",
    )
    parser.add_argument(
        "--max-cost-per-canary",
        type=float,
        default=0.40,
        help="Max cost per canary in USD (default 0.40)",
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Enable credentialed live API probes (default: fail-closed not_run)",
    )
    parser.add_argument(
        "--evidence-path",
        type=Path,
        default=None,
        help="Where to write the evidence JSON",
    )
    return parser.parse_args(argv)


def _emit(evidence: dict[str, Any], evidence_path: Path | None) -> None:
    text = json.dumps(evidence, indent=2, sort_keys=True)
    sys.stdout.write(text + "\n")
    if evidence_path is not None:
        evidence_path.parent.mkdir(parents=True, exist_ok=True)
        evidence_path.write_text(text + "\n", encoding="utf-8")


def _usable_secret(value: str | None) -> bool:
    normalized = (value or "").strip()
    return bool(normalized) and not any(
        normalized.startswith(prefix) for prefix in PLACEHOLDER_PREFIXES
    )


def _env_ready(*names: str) -> bool:
    return all(_usable_secret(os.environ.get(name)) for name in names)


def _probe_gamma() -> dict[str, Any]:
    from scripts.api_clients.gamma_client import GammaClient

    themes = GammaClient().list_themes(limit=1)
    return {"ok": True, "probe": "GammaClient.list_themes", "items_seen": len(themes)}


def _probe_elevenlabs() -> dict[str, Any]:
    from scripts.api_clients.elevenlabs_client import ElevenLabsClient

    voices = ElevenLabsClient().list_voices()
    return {"ok": True, "probe": "ElevenLabsClient.list_voices", "items_seen": len(voices)}


def _probe_canvas() -> dict[str, Any]:
    from scripts.api_clients.canvas_client import CanvasClient

    user = CanvasClient().get_self()
    return {"ok": True, "probe": "CanvasClient.get_self", "id_present": bool(user.get("id"))}


def _probe_qualtrics() -> dict[str, Any]:
    from scripts.api_clients.qualtrics_client import QualtricsClient

    whoami = QualtricsClient().whoami()
    return {"ok": True, "probe": "QualtricsClient.whoami", "id_present": bool(whoami)}


def _probe_panopto() -> dict[str, Any]:
    from scripts.api_clients.panopto_client import PanoptoClient

    token = PanoptoClient().authenticate()
    return {"ok": True, "probe": "PanoptoClient.authenticate", "token_present": bool(token)}


API_PROBES: dict[str, tuple[tuple[str, ...], Callable[[], dict[str, Any]]]] = {
    "gamma": (("GAMMA_API_KEY",), _probe_gamma),
    "elevenlabs": (("ELEVENLABS_API_KEY",), _probe_elevenlabs),
    "canvas": (("CANVAS_API_URL", "CANVAS_ACCESS_TOKEN"), _probe_canvas),
    "qualtrics": (("QUALTRICS_API_TOKEN",), _probe_qualtrics),
    "panopto": (
        ("PANOPTO_BASE_URL", "PANOPTO_CLIENT_ID", "PANOPTO_CLIENT_SECRET"),
        _probe_panopto,
    ),
}


def _run_live_api_probe(name: str) -> dict[str, Any]:
    if name not in API_PROBES:
        return {
            "name": name,
            "status": "skipped_unknown_api",
            "all_ok": True,
            "total_cost_usd": 0.0,
        }
    required_env, probe = API_PROBES[name]
    if not _env_ready(*required_env):
        return {
            "name": name,
            "status": "skipped_missing_credentials",
            "required_env": list(required_env),
            "all_ok": True,
            "total_cost_usd": 0.0,
        }
    try:
        probe_result = probe()
    except APIError as exc:
        return {
            "name": name,
            "status": "failed",
            "all_ok": False,
            "error": str(exc),
            "status_code": exc.status_code,
            "total_cost_usd": 0.0,
        }
    except Exception as exc:  # pragma: no cover - live operator path
        return {
            "name": name,
            "status": "failed",
            "all_ok": False,
            "error": f"{type(exc).__name__}: {exc}",
            "total_cost_usd": 0.0,
        }
    return {
        "name": name,
        "status": "pass",
        "all_ok": bool(probe_result.get("ok")),
        "canaries": [probe_result],
        "total_cost_usd": 0.0,
    }


def _not_run_evidence(
    *,
    api_list: list[str],
    spend_ceiling: float,
    max_canaries_per_api: int,
    max_cost_per_canary: float,
) -> dict[str, Any]:
    return {
        "smoke": "5_api_live_binding",
        "spend_ceiling_usd": round(spend_ceiling, 2),
        "max_canaries_per_api": max_canaries_per_api,
        "max_cost_per_canary_usd": max_cost_per_canary,
        "apis": [{"name": name, "status": "not_run"} for name in api_list],
        "total_spend_usd": 0.0,
        "verdict": "not_run",
        "reason": (
            "fail-closed default; pass --live after loading credentials to invoke "
            "post-Slab-7c API client probes"
        ),
        "generated_at": datetime.now(UTC).isoformat(),
    }


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    api_list = [name.strip() for name in args.apis.split(",") if name.strip()]
    spend_ceiling = len(api_list) * args.max_canaries_per_api * args.max_cost_per_canary
    if not args.live:
        _emit(
            _not_run_evidence(
                api_list=api_list,
                spend_ceiling=spend_ceiling,
                max_canaries_per_api=args.max_canaries_per_api,
                max_cost_per_canary=args.max_cost_per_canary,
            ),
            args.evidence_path,
        )
        return 1

    load_env()
    api_results = [_run_live_api_probe(name) for name in api_list]
    ready_results = [
        row
        for row in api_results
        if row["status"] not in {"skipped_missing_credentials", "skipped_unknown_api"}
    ]
    failed = [row for row in ready_results if not row.get("all_ok")]
    total_spend = round(sum(float(row.get("total_cost_usd", 0.0)) for row in api_results), 2)
    verdict = "PASS" if ready_results and not failed and total_spend <= spend_ceiling else "FAIL"
    if not ready_results:
        verdict = "not_run"
    evidence = {
        "smoke": "5_api_live_binding",
        "spend_ceiling_usd": round(spend_ceiling, 2),
        "max_canaries_per_api": args.max_canaries_per_api,
        "max_cost_per_canary_usd": args.max_cost_per_canary,
        "apis": api_results,
        "total_spend_usd": total_spend,
        "verdict": verdict,
        "reason": (
            "no credential-ready APIs; skipped without spend"
            if verdict == "not_run"
            else "post-Slab-7c API client probes completed"
        ),
        "generated_at": datetime.now(UTC).isoformat(),
    }
    _emit(evidence, args.evidence_path)
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
