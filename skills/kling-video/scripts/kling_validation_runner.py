# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""Run reusable Kling validation cases outside active production bundles."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from kling_operations import run_image_to_video, run_text_to_video

try:
    from scripts.api_clients.kling_client import KlingClient
except ModuleNotFoundError:  # pragma: no cover - optional dependency for mocked test paths
    KlingClient = None  # type: ignore[assignment]

try:
    from scripts.api_clients.kling_public_client import KlingPublicClient
except ModuleNotFoundError:  # pragma: no cover - optional dependency for mocked test paths
    KlingPublicClient = None  # type: ignore[assignment]

load_dotenv(PROJECT_ROOT / ".env")

DEFAULT_CASE_FILE = PROJECT_ROOT / "skills" / "kling-video" / "references" / "validation-cases.yaml"
DEFAULT_OUTPUT_ROOT = PROJECT_ROOT / "reports" / "kling-validation"


class KlingValidationError(RuntimeError):
    """Raised when a validation case cannot be executed safely."""


def _now_utc() -> str:
    return datetime.now(UTC).isoformat()


def load_validation_cases(case_file: Path = DEFAULT_CASE_FILE) -> list[dict[str, Any]]:
    payload = yaml.safe_load(case_file.read_text(encoding="utf-8")) or {}
    cases = payload.get("cases", [])
    if not isinstance(cases, list):
        raise KlingValidationError(f"Invalid case file: {case_file}")
    normalized: list[dict[str, Any]] = []
    for case in cases:
        if isinstance(case, dict):
            normalized.append(case)
    return normalized


def find_cases(case_ids: list[str], *, case_file: Path = DEFAULT_CASE_FILE) -> list[dict[str, Any]]:
    wanted = {value.strip() for value in case_ids if value.strip()}
    all_cases = load_validation_cases(case_file)
    if not wanted:
        return all_cases
    found: list[dict[str, Any]] = []
    for case in all_cases:
        case_id = str(case.get("case_id") or "").strip()
        if case_id in wanted:
            found.append(case)
    missing = wanted.difference({str(case.get("case_id") or "").strip() for case in found})
    if missing:
        raise KlingValidationError(f"Unknown validation case(s): {', '.join(sorted(missing))}")
    return found


def _request_audio_payload(requested_audio_mode: str) -> tuple[bool | None, str]:
    mode = requested_audio_mode.strip().lower()
    if mode in {"", "silent"}:
        return None, "omitted"
    if mode in {"native", "sound-on", "audio-on", "native-sfx", "native_ambience", "native-ambience"}:
        return True, "sound=true"
    raise KlingValidationError(f"Unsupported requested_audio_mode: {requested_audio_mode}")


def _sanitize(value: str) -> str:
    chars: list[str] = []
    for char in value.lower():
        if char.isalnum() or char in {"-", "_"}:
            chars.append(char)
        else:
            chars.append("-")
    return "".join(chars).strip("-")


def _request_fingerprint(payload: dict[str, Any]) -> str:
    serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()[:16]


def _build_client(api_surface: str) -> Any:
    normalized = api_surface.strip().lower()
    if normalized in {"", "current_repo_client"}:
        if KlingClient is None:
            raise KlingValidationError("Current repo Kling client is unavailable")
        return KlingClient()
    if normalized == "newer_public_surface":
        if KlingPublicClient is None:
            raise KlingValidationError("Public-surface Kling client is unavailable")
        return KlingPublicClient()
    raise KlingValidationError(f"Unsupported api_surface: {api_surface}")


def _validate_local_mp4(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise KlingValidationError(f"Generated file is missing: {path}")
    if path.suffix.lower() != ".mp4":
        raise KlingValidationError(f"Generated file is not an MP4: {path}")
    size = path.stat().st_size
    if size <= 0:
        raise KlingValidationError(f"Generated file is empty: {path}")
    return {
        "exists": True,
        "suffix_is_mp4": True,
        "non_zero_size": True,
        "file_size_bytes": size,
    }


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _default_filename(case: dict[str, Any]) -> str:
    case_id = _sanitize(str(case.get("case_id") or "case"))
    model = _sanitize(str(case.get("model_name") or "model"))
    mode = _sanitize(str(case.get("mode") or "std"))
    duration = _sanitize(str(case.get("duration") or "5"))
    return f"{case_id}__{model}_{mode}_{duration}s.mp4"


def execute_validation_case(
    case: dict[str, Any],
    *,
    output_dir: Path,
    image_url_override: str | None = None,
    client: Any = None,
) -> dict[str, Any]:
    case_id = str(case.get("case_id") or "").strip()
    if not case_id:
        raise KlingValidationError("Validation case is missing case_id")

    operation = str(case.get("operation") or "").strip().lower()
    if operation not in {"text2video", "image2video"}:
        raise KlingValidationError(f"Unsupported validation operation for {case_id}: {operation}")

    requested_audio_mode = str(case.get("requested_audio_mode") or "silent")
    sound_value, api_audio_field = _request_audio_payload(requested_audio_mode)

    request_payload = {
        "operation": operation,
        "api_surface": str(case.get("api_surface") or "current_repo_client"),
        "model_name": str(case.get("model_name") or "kling-v2-6"),
        "mode": str(case.get("mode") or "std"),
        "duration": str(case.get("duration") or "5"),
        "aspect_ratio": str(case.get("aspect_ratio") or "16:9"),
        "requested_audio_mode": requested_audio_mode,
        "api_audio_field": api_audio_field,
        "prompt": str(case.get("prompt") or ""),
    }
    policy = {
        "lane": str(case.get("lane") or "validation-only"),
        "production_safe": bool(case.get("production_safe", False)),
        "promotion_status": str(case.get("promotion_status") or "non-promoting"),
        "audio_policy": str(case.get("audio_policy") or ""),
    }

    try:
        if client is None:
            client = _build_client(request_payload["api_surface"])
        if operation == "image2video":
            image_url = image_url_override or case.get("image_url")
            if not image_url:
                raise KlingValidationError(
                    f"Validation case {case_id} requires image_url. "
                    "Provide --image-url or populate image_url in the case file."
                )
            request_payload["image_url"] = str(image_url)

        fingerprint = _request_fingerprint(request_payload)
        filename = _default_filename(case)
        if operation == "text2video":
            result = run_text_to_video(
                request_payload["prompt"],
                model_name=request_payload["model_name"],
                duration=request_payload["duration"],
                aspect_ratio=request_payload["aspect_ratio"],
                mode=request_payload["mode"],
                sound=sound_value,
                output_dir=output_dir,
                filename=filename,
                client=client,
            )
        else:
            result = run_image_to_video(
                str(request_payload["image_url"]),
                prompt=request_payload["prompt"],
                model_name=request_payload["model_name"],
                duration=request_payload["duration"],
                aspect_ratio=request_payload["aspect_ratio"],
                mode=request_payload["mode"],
                sound=sound_value,
                output_dir=output_dir,
                filename=filename,
                client=client,
            )
        output_path = Path(str(result["output_path"]))
        local_validation = _validate_local_mp4(output_path)
        receipt = {
            "case_id": case_id,
            "status": "success",
            "executed_at_utc": _now_utc(),
            "request_fingerprint": fingerprint,
            "request": request_payload,
            "policy": policy,
            "task_id": result.get("task_id"),
            "video_url": result.get("video_url"),
            "video_duration": result.get("video_duration"),
            "output_path": str(output_path),
            "local_validation": local_validation,
            "generation_choices": result.get("generation_choices"),
            "task_data": result.get("task_data"),
            "environment": {
                "python": platform.python_version(),
                "script": str(Path(__file__).resolve()),
            },
        }
    except Exception as exc:
        fingerprint = _request_fingerprint(request_payload)
        receipt = {
            "case_id": case_id,
            "status": "error",
            "executed_at_utc": _now_utc(),
            "request_fingerprint": fingerprint,
            "request": request_payload,
            "policy": policy,
            "error": str(exc),
            "environment": {
                "python": platform.python_version(),
                "script": str(Path(__file__).resolve()),
            },
        }
        status_code = getattr(exc, "status_code", None)
        response_body = getattr(exc, "response_body", None)
        if status_code is not None:
            receipt["status_code"] = status_code
        if response_body is not None:
            receipt["response_body"] = response_body

    return receipt


def run_validation_cases(
    case_ids: list[str],
    *,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    run_label: str | None = None,
    case_file: Path = DEFAULT_CASE_FILE,
    image_url_override: str | None = None,
    client: Any = None,
) -> dict[str, Any]:
    cases = find_cases(case_ids, case_file=case_file)
    label = run_label or datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = output_root / label
    receipts_dir = run_dir / "receipts"
    receipts_dir.mkdir(parents=True, exist_ok=True)

    receipts: list[dict[str, Any]] = []
    for case in cases:
        receipt = execute_validation_case(
            case,
            output_dir=run_dir,
            image_url_override=image_url_override,
            client=client,
        )
        receipts.append(receipt)
        _write_json(receipts_dir / f"{_sanitize(str(case.get('case_id') or 'case'))}.json", receipt)

    summary = {
        "run_label": label,
        "generated_at_utc": _now_utc(),
        "case_file": str(case_file),
        "output_dir": str(run_dir),
        "requested_case_ids": case_ids,
        "success_count": sum(1 for receipt in receipts if receipt["status"] == "success"),
        "error_count": sum(1 for receipt in receipts if receipt["status"] == "error"),
        "cases": [
            {
                "case_id": receipt["case_id"],
                "status": receipt["status"],
                "task_id": receipt.get("task_id"),
                "output_path": receipt.get("output_path"),
            }
            for receipt in receipts
        ],
    }
    _write_json(run_dir / "summary.json", summary)
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run reusable Kling validation cases.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="List available validation cases.")
    list_parser.add_argument("--case-file", type=Path, default=DEFAULT_CASE_FILE)

    run_parser = subparsers.add_parser("run", help="Execute one or more validation cases.")
    run_parser.add_argument("--case-id", action="append", default=[])
    run_parser.add_argument("--case-file", type=Path, default=DEFAULT_CASE_FILE)
    run_parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    run_parser.add_argument("--run-label")
    run_parser.add_argument("--image-url")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "list":
        cases = load_validation_cases(args.case_file)
        payload = {
            "case_file": str(args.case_file),
            "cases": [
                {
                    "case_id": case.get("case_id"),
                    "operation": case.get("operation"),
                    "model_name": case.get("model_name"),
                    "mode": case.get("mode"),
                    "requested_audio_mode": case.get("requested_audio_mode"),
                    "description": case.get("description"),
                }
                for case in cases
            ],
        }
        print(json.dumps(payload, indent=2))
        return 0

    if args.command == "run":
        summary = run_validation_cases(
            list(args.case_id),
            output_root=args.output_root,
            run_label=args.run_label,
            case_file=args.case_file,
            image_url_override=args.image_url,
        )
        print(json.dumps(summary, indent=2))
        return 0 if summary["error_count"] == 0 else 1

    parser.error(f"Unsupported command: {args.command}")
    return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
