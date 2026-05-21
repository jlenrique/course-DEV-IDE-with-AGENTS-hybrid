# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""Agent-level Kling operations wrapper.

Bridges Kira's generation decisions and the KlingClient API layer.
Handles submission, polling, extraction of video URLs, download, and
structured result formatting for Marcus/Kira workflows.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv

from scripts.utilities.motion_budgeting import (
    estimate_motion_credits,
    normalize_motion_mode,
)

try:
    from scripts.api_clients.kling_client import KlingClient
except ModuleNotFoundError:  # pragma: no cover - optional dependency for mocked test paths
    KlingClient = None  # type: ignore[assignment]

load_dotenv(PROJECT_ROOT / ".env")

logger = logging.getLogger(__name__)

STAGING_DIR = PROJECT_ROOT / "course-content" / "staging"


def _extract_video_url(task_data: dict[str, Any]) -> str | None:
    """Extract the first video URL from a completed Kling task response."""
    data = task_data.get("data", {})
    task_result = data.get("task_result", {})
    videos = task_result.get("videos", [])
    if isinstance(videos, list) and videos:
        first = videos[0]
        if isinstance(first, dict):
            return first.get("url")
    return None


def _extract_duration(task_data: dict[str, Any]) -> str | None:
    """Extract duration from a completed Kling task response."""
    data = task_data.get("data", {})
    task_result = data.get("task_result", {})
    videos = task_result.get("videos", [])
    if isinstance(videos, list) and videos:
        first = videos[0]
        if isinstance(first, dict):
            return first.get("duration")
    return None


def resolve_motion_mode(
    *,
    duration_seconds: float,
    motion_budget: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Apply Epic 14 budget guardrails, including one-step pro -> std downgrade."""
    budget = motion_budget or {}
    preferred = normalize_motion_mode(str(budget.get("model_preference") or "std"))
    max_credits = budget.get("max_credits")
    estimated = estimate_motion_credits(duration_seconds, preferred)
    downgraded_from: str | None = None

    if isinstance(max_credits, (int, float)) and estimated > float(max_credits):
        if preferred == "pro":
            downgraded_from = "pro"
            preferred = "std"
            estimated = estimate_motion_credits(duration_seconds, preferred)
        if estimated > float(max_credits):
            raise RuntimeError(
                "Motion clip exceeds budget ceiling even after downgrade "
                f"(estimated={estimated}, max_credits={max_credits})"
            )

    return {
        "mode": preferred,
        "estimated_credits": estimated,
        "downgraded_from": downgraded_from,
    }


def run_text_to_video(
    prompt: str,
    *,
    model_name: str = "kling-v1-6",
    duration: str = "5",
    aspect_ratio: str = "16:9",
    mode: str = "std",
    negative_prompt: str | None = None,
    sound: bool | None = None,
    output_dir: Path | str | None = None,
    filename: str | None = None,
    client: KlingClient | None = None,
) -> dict[str, Any]:
    """Execute a full text-to-video generation and download.

    Returns a structured dict with task metadata, chosen parameters,
    extracted video URL, and local download path.
    """
    if client is None:
        if KlingClient is None:
            raise RuntimeError("KlingClient dependencies are unavailable; install API client extras")
        client = KlingClient()
    if output_dir is None:
        output_dir = STAGING_DIR
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    request_kwargs: dict[str, Any] = {
        "model_name": model_name,
        "duration": duration,
        "aspect_ratio": aspect_ratio,
        "mode": mode,
        "negative_prompt": negative_prompt,
    }
    if sound is not None:
        request_kwargs["sound"] = sound
    submitted = client.text_to_video(prompt, **request_kwargs)
    task_id = submitted.get("data", {}).get("task_id") or submitted.get("task_id")
    if not task_id:
        raise RuntimeError(f"No task_id in response: {submitted}")

    completed = client.wait_for_completion(task_id, task_type="text2video")
    video_url = _extract_video_url(completed)
    if not video_url:
        raise RuntimeError(f"No video URL found in completed task: {completed}")

    if filename is None:
        filename = f"{task_id}.mp4"
    output_path = client.download_video(video_url, output_dir / filename)

    return {
        "task_id": task_id,
        "operation": "text2video",
        "generation_choices": {
            "model_name": model_name,
            "duration": duration,
            "aspect_ratio": aspect_ratio,
            "mode": mode,
            "negative_prompt": negative_prompt,
            "sound": sound,
        },
        "video_url": video_url,
        "video_duration": _extract_duration(completed),
        "output_path": str(output_path),
        "task_data": completed,
    }


def run_image_to_video(
    image_url: str,
    *,
    prompt: str = "",
    model_name: str = "kling-v2-6",
    duration: str = "5",
    aspect_ratio: str = "16:9",
    mode: str = "std",
    end_image_url: str | None = None,
    negative_prompt: str | None = None,
    sound: bool | None = None,
    output_dir: Path | str | None = None,
    filename: str | None = None,
    client: KlingClient | None = None,
) -> dict[str, Any]:
    """Execute a full image-to-video generation and download."""
    if client is None:
        if KlingClient is None:
            raise RuntimeError("KlingClient dependencies are unavailable; install API client extras")
        client = KlingClient()
    if output_dir is None:
        output_dir = STAGING_DIR
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    request_kwargs = {
        "prompt": prompt,
        "model_name": model_name,
        "duration": duration,
        "aspect_ratio": aspect_ratio,
        "mode": mode,
        "end_image_url": end_image_url,
        "negative_prompt": negative_prompt,
    }
    if sound is not None:
        request_kwargs["sound"] = sound
    submitted = client.image_to_video(image_url, **request_kwargs)
    task_id = submitted.get("data", {}).get("task_id") or submitted.get("task_id")
    if not task_id:
        raise RuntimeError(f"No task_id in response: {submitted}")

    completed = client.wait_for_completion(task_id, task_type="image2video")
    video_url = _extract_video_url(completed)
    if not video_url:
        raise RuntimeError(f"No video URL found in completed task: {completed}")

    if filename is None:
        filename = f"{task_id}.mp4"
    output_path = client.download_video(video_url, output_dir / filename)

    return {
        "task_id": task_id,
        "operation": "image2video",
        "generation_choices": {
            "model_name": model_name,
            "duration": duration,
            "aspect_ratio": aspect_ratio,
            "mode": mode,
            "negative_prompt": negative_prompt,
            "end_image_url": end_image_url,
            "sound": sound,
        },
        "video_url": video_url,
        "video_duration": _extract_duration(completed),
        "output_path": str(output_path),
        "task_data": completed,
    }


def run_lip_sync(
    video_url: str,
    audio_url: str,
    *,
    output_dir: Path | str | None = None,
    filename: str | None = None,
    client: KlingClient | None = None,
) -> dict[str, Any]:
    """Execute a full lip-sync run and download."""
    if client is None:
        if KlingClient is None:
            raise RuntimeError("KlingClient dependencies are unavailable; install API client extras")
        client = KlingClient()
    if output_dir is None:
        output_dir = STAGING_DIR
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    submitted = client.lip_sync(video_url, audio_url)
    task_id = submitted.get("data", {}).get("task_id") or submitted.get("task_id")
    if not task_id:
        raise RuntimeError(f"No task_id in response: {submitted}")

    completed = client.wait_for_completion(task_id, task_type="lip-sync")
    output_video_url = _extract_video_url(completed)
    if not output_video_url:
        raise RuntimeError(f"No video URL found in completed task: {completed}")

    if filename is None:
        filename = f"{task_id}.mp4"
    output_path = client.download_video(output_video_url, output_dir / filename)

    return {
        "task_id": task_id,
        "operation": "lip-sync",
        "video_url": output_video_url,
        "video_duration": _extract_duration(completed),
        "output_path": str(output_path),
        "task_data": completed,
    }


def generate_motion_clip(
    slide_motion_request: dict[str, Any],
    *,
    motion_budget: dict[str, Any] | None = None,
    output_dir: Path | str | None = None,
    client: KlingClient | None = None,
) -> dict[str, Any]:
    """Generate a silent motion clip for one Gate 2M video-designated slide.

    Prefers image-to-video when an image URL is supplied; otherwise falls back
    to text-to-video from the motion brief.
    """
    slide_id = str(slide_motion_request.get("slide_id") or "").strip()
    if not slide_id:
        raise RuntimeError("slide_motion_request requires slide_id")

    duration_seconds = float(slide_motion_request.get("motion_duration_seconds") or 5.0)
    mode_result = resolve_motion_mode(
        duration_seconds=duration_seconds,
        motion_budget=motion_budget,
    )

    source_image_url = (
        slide_motion_request.get("source_image_url")
        or slide_motion_request.get("image_url")
        or slide_motion_request.get("slide_image_url")
    )
    motion_brief = str(slide_motion_request.get("motion_brief") or "").strip()
    narration_intent = str(slide_motion_request.get("narration_intent") or "").strip()
    prompt = motion_brief
    if narration_intent:
        prompt = f"{motion_brief}. Narration intent: {narration_intent}".strip(". ")

    if source_image_url:
        result = run_image_to_video(
            str(source_image_url),
            prompt=prompt,
            duration=str(int(round(duration_seconds))),
            mode=mode_result["mode"],
            output_dir=output_dir,
            filename=f"{slide_id}_motion.mp4",
            client=client,
        )
    else:
        result = run_text_to_video(
            prompt or f"Educational motion clip for {slide_id}",
            duration=str(int(round(duration_seconds))),
            mode=mode_result["mode"],
            output_dir=output_dir,
            filename=f"{slide_id}_motion.mp4",
            client=client,
        )

    return {
        "slide_id": slide_id,
        "mp4_path": result["output_path"],
        "model_used": mode_result["mode"],
        "duration_seconds": float(result.get("video_duration") or duration_seconds),
        "credits_consumed": mode_result["estimated_credits"],
        "self_assessment": (
            "image-to-video used from approved slide art"
            if source_image_url
            else "text-to-video fallback used because no source image URL was provided"
        ),
        "operation": result["operation"],
        "downgraded_from": mode_result["downgraded_from"],
        "task_id": result["task_id"],
    }


def build_parser() -> argparse.ArgumentParser:
    """Build CLI parser for agent-invoked use and self-documentation."""
    parser = argparse.ArgumentParser(
        description="Run Kling video operations and return structured JSON."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    text = subparsers.add_parser("text2video", help="Generate video from text prompt")
    text.add_argument("prompt", help="Video prompt")
    text.add_argument("--model-name", default="kling-v1-6")
    text.add_argument("--duration", default="5")
    text.add_argument("--aspect-ratio", default="16:9")
    text.add_argument("--mode", default="std")
    text.add_argument("--negative-prompt")
    text.add_argument("--output-dir")
    text.add_argument("--filename")

    image = subparsers.add_parser("image2video", help="Generate video from source image")
    image.add_argument("image_url", help="Source image URL")
    image.add_argument("--prompt", default="")
    image.add_argument("--model-name", default="kling-v2-6")
    image.add_argument("--duration", default="5")
    image.add_argument("--aspect-ratio", default="16:9")
    image.add_argument("--mode", default="std")
    image.add_argument("--end-image-url")
    image.add_argument("--negative-prompt")
    image.add_argument("--output-dir")
    image.add_argument("--filename")

    lip = subparsers.add_parser("lip-sync", help="Generate lip-synced video")
    lip.add_argument("video_url", help="Source video URL")
    lip.add_argument("audio_url", help="Audio URL")
    lip.add_argument("--output-dir")
    lip.add_argument("--filename")

    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entry point returning meaningful exit codes."""
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "text2video":
            result = run_text_to_video(
                args.prompt,
                model_name=args.model_name,
                duration=args.duration,
                aspect_ratio=args.aspect_ratio,
                mode=args.mode,
                negative_prompt=args.negative_prompt,
                output_dir=args.output_dir,
                filename=args.filename,
            )
        elif args.command == "image2video":
            result = run_image_to_video(
                args.image_url,
                prompt=args.prompt,
                model_name=args.model_name,
                duration=args.duration,
                aspect_ratio=args.aspect_ratio,
                mode=args.mode,
                end_image_url=args.end_image_url,
                negative_prompt=args.negative_prompt,
                output_dir=args.output_dir,
                filename=args.filename,
            )
        else:
            result = run_lip_sync(
                args.video_url,
                args.audio_url,
                output_dir=args.output_dir,
                filename=args.filename,
            )
        print(json.dumps(result, indent=2))
        return 0
    except Exception as exc:  # pragma: no cover - CLI failure path
        print(
            json.dumps(
                {
                    "status": "error",
                    "error": str(exc),
                    "command": args.command,
                },
                indent=2,
            )
        )
        return 1


if __name__ == "__main__":  # pragma: no cover - CLI entry
    sys.exit(main())
