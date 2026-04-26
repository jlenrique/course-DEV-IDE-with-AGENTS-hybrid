# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""Internal Gate 7E Kling backend for one motion-plan slide.

The production-facing entrypoint lives under
``skills/production-coordination/scripts/run_motion_generation.py``.
This backend owns one lifecycle only:
submit or resume -> poll -> download -> validate -> patch motion_plan.yaml.

It fails closed. If terminal success and local validation do not both complete,
the motion-plan row remains unresolved for Motion Gate.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
SCRIPT_DIR = Path(__file__).resolve().parent
MOTION_PLAN_DIR = PROJECT_ROOT / "skills" / "production-coordination" / "scripts"
for extra in (SCRIPT_DIR, MOTION_PLAN_DIR):
    if str(extra) not in sys.path:
        sys.path.insert(0, str(extra))

try:
    from scripts.api_clients.kling_client import KlingClient
except ModuleNotFoundError:  # pragma: no cover - allows mocked/unit-only paths
    KlingClient = None  # type: ignore[assignment]
from kling_operations import (
    _extract_duration,
    _extract_video_url,
    resolve_motion_mode,
)
from motion_plan import (
    load_motion_plan,
    write_motion_plan,
)

load_dotenv(PROJECT_ROOT / ".env")

DEFAULT_POLL_INTERVAL = 10
DEFAULT_MAX_ATTEMPTS = 90
DEFAULT_TIMEOUT_SECONDS = 1800


class MotionGenerationError(RuntimeError):
    """Raised when Gate 7E generation cannot complete safely."""


def _now_utc() -> str:
    return datetime.now(UTC).isoformat()


def _sanitize(value: str) -> str:
    allowed = []
    for char in value.lower():
        if char.isalnum() or char in {"-", "_"}:
            allowed.append(char)
        else:
            allowed.append("-")
    return "".join(allowed).strip("-")


def _receipt_stem(row: dict[str, Any]) -> str:
    card_number = row.get("card_number")
    if isinstance(card_number, int):
        return f"motion-generation-slide-{card_number:02d}"
    if isinstance(card_number, float) and card_number.is_integer():
        return f"motion-generation-slide-{int(card_number):02d}"
    slide_id = str(row.get("slide_id") or "").strip()
    return f"motion-generation-{_sanitize(slide_id)}"


def _receipt_paths(bundle_dir: Path, row: dict[str, Any]) -> dict[str, Path]:
    stem = _receipt_stem(row)
    return {
        "progress": bundle_dir / f"{stem}.progress.json",
        "result": bundle_dir / f"{stem}.json",
        "lock": bundle_dir / f"{stem}.lock",
    }


def _write_json(path: Path, payload: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def _acquire_lock(path: Path, *, slide_id: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as handle:
        handle.write(json.dumps({"slide_id": slide_id, "started_at_utc": _now_utc()}, indent=2))


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _resolve_local_path(path_value: str | None, *, repo_root: Path) -> Path | None:
    if not path_value:
        return None
    path = Path(path_value)
    if path.is_absolute():
        return path
    return repo_root / path


def _to_repo_relative(path: Path, *, repo_root: Path) -> str:
    return str(path.resolve().relative_to(repo_root.resolve())).replace("\\", "/")


def _validate_local_mp4(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise MotionGenerationError(f"Downloaded motion asset is missing: {path}")
    if path.suffix.lower() != ".mp4":
        raise MotionGenerationError(f"Motion asset must be .mp4: {path}")
    size = path.stat().st_size
    if size <= 0:
        raise MotionGenerationError(f"Downloaded motion asset is empty: {path}")
    return {
        "path": str(path),
        "file_size_bytes": size,
        "checks": {
            "exists": True,
            "suffix_is_mp4": True,
            "non_zero_size": True,
        },
    }


def _find_slide_row(motion_plan: dict[str, Any], slide_id: str) -> dict[str, Any]:
    for row in motion_plan.get("slides", []):
        if isinstance(row, dict) and str(row.get("slide_id") or "").strip() == slide_id:
            return row
    raise MotionGenerationError(f"slide_id not found in motion plan: {slide_id}")


def _recompute_summary(motion_plan: dict[str, Any]) -> None:
    static_count = 0
    video_count = 0
    animation_count = 0
    estimated_credits = 0.0
    consumed_credits = 0.0
    for row in motion_plan.get("slides", []):
        if not isinstance(row, dict):
            continue
        motion_type = str(row.get("motion_type") or "static").strip().lower() or "static"
        if motion_type == "video":
            video_count += 1
        elif motion_type == "animation":
            animation_count += 1
        else:
            static_count += 1
        estimate = row.get("estimated_credits")
        if isinstance(estimate, (int, float)):
            estimated_credits += float(estimate)
        consumed = row.get("credits_consumed")
        if isinstance(consumed, (int, float)):
            consumed_credits += float(consumed)
    motion_plan["summary"] = {
        "static": static_count,
        "video": video_count,
        "animation": animation_count,
        "estimated_credits": round(estimated_credits, 2),
        "credits_consumed": round(consumed_credits, 2),
    }


def _is_terminal_row(row: dict[str, Any], *, repo_root: Path) -> bool:
    status = str(row.get("motion_status") or "").strip().lower()
    if status not in {"generated", "approved"}:
        return False
    local_asset = _resolve_local_path(str(row.get("motion_asset_path") or "").strip(), repo_root=repo_root)
    if local_asset is None:
        return False
    try:
        _validate_local_mp4(local_asset)
    except MotionGenerationError:
        return False
    return True


def _extract_provider_status(task_data: dict[str, Any]) -> str:
    data_block = task_data.get("data", {}) if isinstance(task_data.get("data"), dict) else {}
    return str(
        task_data.get("status")
        or data_block.get("status")
        or data_block.get("task_status")
        or ""
    ).strip()


def _default_model_name(operation: str) -> str:
    return "kling-v2-6" if operation in {"text2video", "image2video"} else "kling-v2-6"


def _build_prompt(row: dict[str, Any]) -> str:
    motion_brief = str(row.get("motion_brief") or "").strip()
    narration_intent = str(row.get("narration_intent") or "").strip()
    if motion_brief and narration_intent:
        return f"{motion_brief}. Narration intent: {narration_intent}".strip()
    return motion_brief or f"Educational motion clip for {row.get('slide_id')}"


def _submit_generation(
    row: dict[str, Any],
    *,
    motion_budget: dict[str, Any] | None,
    client: KlingClient,
) -> dict[str, Any]:
    duration_seconds = float(row.get("motion_duration_seconds") or 5.0)
    mode_result = resolve_motion_mode(
        duration_seconds=duration_seconds,
        motion_budget=motion_budget,
    )
    source_image_url = (
        row.get("source_image_url")
        or row.get("image_url")
        or row.get("slide_image_url")
    )
    prompt = _build_prompt(row)
    operation = "image2video" if source_image_url else "text2video"
    model_name = str(row.get("model_name") or _default_model_name(operation))
    duration_token = str(int(round(duration_seconds)))
    if operation == "image2video":
        response = client.image_to_video(
            str(source_image_url),
            prompt=prompt,
            model_name=model_name,
            duration=duration_token,
            aspect_ratio="16:9",
            mode=mode_result["mode"],
        )
    else:
        response = client.text_to_video(
            prompt,
            model_name=model_name,
            duration=duration_token,
            aspect_ratio="16:9",
            mode=mode_result["mode"],
        )
    task_id = response.get("data", {}).get("task_id") or response.get("task_id")
    if not task_id:
        raise MotionGenerationError(f"No task_id returned for slide {row['slide_id']}")
    return {
        "task_id": str(task_id),
        "operation": operation,
        "model_name": model_name,
        "mode": mode_result["mode"],
        "downgraded_from": mode_result["downgraded_from"],
        "estimated_credits": mode_result["estimated_credits"],
        "requested_duration_seconds": duration_seconds,
        "source_image_url": str(source_image_url) if source_image_url else None,
        "prompt": prompt,
        "requested_audio_mode": "silent",
        "api_audio_field": "omitted",
    }


def _build_success_receipt(
    row: dict[str, Any],
    submission: dict[str, Any],
    completed: dict[str, Any],
    output_path: Path,
    validation: dict[str, Any],
) -> dict[str, Any]:
    data_block = completed.get("data", {}) if isinstance(completed.get("data"), dict) else {}
    provider_credits = data_block.get("task_info", {}).get("external_task_info", {}).get("entity", {}).get("final_unit_deduction")
    duration_value = _extract_duration(completed)
    duration_seconds = float(duration_value) if duration_value not in (None, "") else float(submission["requested_duration_seconds"])
    return {
        "status": "generated",
        "generated_at_utc": _now_utc(),
        "slide_id": row["slide_id"],
        "task_id": submission["task_id"],
        "provider_status": _extract_provider_status(completed),
        "operation": submission["operation"],
        "model_name": submission["model_name"],
        "mode": submission["mode"],
        "downgraded_from": submission["downgraded_from"],
        "requested_audio_mode": submission.get("requested_audio_mode"),
        "api_audio_field": submission.get("api_audio_field"),
        "duration_seconds": duration_seconds,
        "credits_consumed": float(provider_credits) if isinstance(provider_credits, (int, float)) else float(submission["estimated_credits"]),
        "output_path": str(output_path),
        "video_url": _extract_video_url(completed),
        "provider_created_at": data_block.get("created_at"),
        "provider_updated_at": data_block.get("updated_at"),
        "provider_final_unit_deduction": provider_credits,
        "technical_validation": validation,
        "resume_source": submission.get("resume_source"),
    }


def _patch_row_success(
    motion_plan: dict[str, Any],
    row: dict[str, Any],
    receipt: dict[str, Any],
    *,
    repo_root: Path,
    result_path: Path,
) -> None:
    row["motion_source"] = "kling"
    row["motion_asset_path"] = _to_repo_relative(Path(receipt["output_path"]), repo_root=repo_root)
    row["motion_duration_seconds"] = float(receipt["duration_seconds"])
    row["motion_status"] = "generated"
    row["credits_consumed"] = float(receipt["credits_consumed"])
    row["provider_task_id"] = receipt["task_id"]
    row["model_used"] = receipt["model_name"]
    row["generation_receipt_path"] = _to_repo_relative(result_path, repo_root=repo_root)
    row["generated_at_utc"] = receipt["generated_at_utc"]
    row["technical_validation"] = receipt["technical_validation"]
    row["last_generation_error"] = None
    _recompute_summary(motion_plan)


def _patch_row_failure(motion_plan: dict[str, Any], row: dict[str, Any], error: str) -> None:
    row["last_generation_error"] = error
    row["last_generation_attempt_utc"] = _now_utc()
    _recompute_summary(motion_plan)


def _load_resume_submission(progress_path: Path) -> dict[str, Any] | None:
    if not progress_path.exists():
        return None
    progress = _load_json(progress_path)
    status = str(progress.get("status") or "").strip().lower()
    task_id = str(progress.get("task_id") or "").strip()
    if status not in {"submitted", "processing"} or not task_id:
        return None
    progress.setdefault("downgraded_from", None)
    progress["resume_source"] = "progress"
    return progress


def run_motion_generation_for_slide(
    *,
    motion_plan_path: str | Path,
    slide_id: str,
    bundle_dir: str | Path | None = None,
    repo_root: Path = PROJECT_ROOT,
    client: KlingClient | None = None,
    poll_interval: int = DEFAULT_POLL_INTERVAL,
    max_attempts: int = DEFAULT_MAX_ATTEMPTS,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    motion_plan_file = Path(motion_plan_path)
    if bundle_dir is None:
        bundle = motion_plan_file.parent
    else:
        bundle = Path(bundle_dir)
    motion_dir = bundle / "motion"
    motion_dir.mkdir(parents=True, exist_ok=True)

    motion_plan = load_motion_plan(motion_plan_file)
    row = _find_slide_row(motion_plan, slide_id)
    if str(row.get("motion_type") or "").strip().lower() != "video":
        raise MotionGenerationError(f"slide {slide_id} is not designated as video")

    receipts = _receipt_paths(bundle, row)
    try:
        _acquire_lock(receipts["lock"], slide_id=slide_id)
    except FileExistsError as exc:
        raise MotionGenerationError(f"Another motion-generation runner is already active for {slide_id}") from exc

    try:
        if _is_terminal_row(row, repo_root=repo_root):
            existing = {
                "status": "existing",
                "slide_id": slide_id,
                "motion_asset_path": row.get("motion_asset_path"),
                "motion_status": row.get("motion_status"),
                "provider_task_id": row.get("provider_task_id"),
            }
            _write_json(receipts["result"], existing)
            return existing

        if client is None:
            if KlingClient is None:
                raise MotionGenerationError("KlingClient dependencies are unavailable")
            client = KlingClient()

        submission = _load_resume_submission(receipts["progress"])
        if submission is None:
            submission = _submit_generation(
                row,
                motion_budget=motion_plan.get("motion_budget"),
                client=client,
            )
            submission["status"] = "submitted"
            submission["slide_id"] = slide_id
            submission["submitted_at_utc"] = _now_utc()
            _write_json(receipts["progress"], submission)

        completed = client.wait_for_completion(
            submission["task_id"],
            task_type=submission["operation"],
            poll_interval=poll_interval,
            max_attempts=max_attempts,
            timeout_seconds=timeout_seconds,
        )
        video_url = _extract_video_url(completed)
        if not video_url:
            raise MotionGenerationError(f"No video URL found for completed task {submission['task_id']}")

        output_path = motion_dir / f"{slide_id}_motion.mp4"
        downloaded = Path(client.download_video(video_url, output_path))
        validation = _validate_local_mp4(downloaded)
        receipt = _build_success_receipt(row, submission, completed, downloaded, validation)
        _write_json(receipts["progress"], {
            "status": "completed",
            "task_id": receipt["task_id"],
            "provider_status": receipt["provider_status"],
            "duration_seconds": receipt["duration_seconds"],
            "credits_consumed": receipt["credits_consumed"],
            "output_path": receipt["output_path"],
        })
        _write_json(receipts["result"], receipt)
        _patch_row_success(
            motion_plan,
            row,
            receipt,
            repo_root=repo_root,
            result_path=receipts["result"],
        )
        write_motion_plan(motion_plan_file, motion_plan)
        return receipt
    except Exception as exc:
        error_text = str(exc)
        _write_json(
            receipts["result"],
            {
                "status": "error",
                "slide_id": slide_id,
                "error": error_text,
                "generated_at_utc": _now_utc(),
                "requested_audio_mode": "silent",
                "api_audio_field": "omitted",
            },
        )
        _patch_row_failure(motion_plan, row, error_text)
        write_motion_plan(motion_plan_file, motion_plan)
        raise
    finally:
        receipts["lock"].unlink(missing_ok=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run one internal Gate 7E Kling generation backend.")
    parser.add_argument("--motion-plan", required=True, type=Path)
    parser.add_argument("--slide-id", required=True)
    parser.add_argument("--bundle-dir", type=Path, default=None)
    parser.add_argument("--poll-interval", type=int, default=DEFAULT_POLL_INTERVAL)
    parser.add_argument("--max-attempts", type=int, default=DEFAULT_MAX_ATTEMPTS)
    parser.add_argument("--timeout-seconds", type=int, default=DEFAULT_TIMEOUT_SECONDS)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = run_motion_generation_for_slide(
            motion_plan_path=args.motion_plan,
            slide_id=args.slide_id,
            bundle_dir=args.bundle_dir,
            poll_interval=args.poll_interval,
            max_attempts=args.max_attempts,
            timeout_seconds=args.timeout_seconds,
        )
        print(json.dumps(result, indent=2))
        return 0
    except Exception as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, indent=2))
        return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
