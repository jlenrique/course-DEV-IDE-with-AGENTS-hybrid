# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""Post-process Kling motion clips into delivery-ready variants."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from scripts.utilities.ffmpeg import resolve_ffmpeg_binary


def build_slow_tail_filter(
    *,
    normal_seconds: float,
    slow_tail_output_seconds: float,
    tail_source_seconds: float,
) -> str:
    """Build an ffmpeg filter that appends a slowed tail to the clip."""
    if normal_seconds <= 0:
        raise ValueError("normal_seconds must be positive")
    if slow_tail_output_seconds <= 0:
        raise ValueError("slow_tail_output_seconds must be positive")
    if tail_source_seconds <= 0:
        raise ValueError("tail_source_seconds must be positive")
    if tail_source_seconds > normal_seconds:
        raise ValueError("tail_source_seconds cannot exceed normal_seconds")

    tail_start = normal_seconds - tail_source_seconds
    slow_factor = slow_tail_output_seconds / tail_source_seconds
    return (
        f"[0:v]trim=start=0:end={normal_seconds:.3f},setpts=PTS-STARTPTS[v0];"
        f"[0:v]trim=start={tail_start:.3f}:end={normal_seconds:.3f},"
        f"setpts={slow_factor:.6f}*(PTS-STARTPTS)[v1];"
        f"[v0][v1]concat=n=2:v=1:a=0[outv]"
    )


def build_slow_tail_command(
    *,
    ffmpeg_binary: str,
    input_path: str | Path,
    output_path: str | Path,
    normal_seconds: float,
    slow_tail_output_seconds: float,
    tail_source_seconds: float,
) -> list[str]:
    """Build the ffmpeg command for a slowed-tail derived clip."""
    filter_graph = build_slow_tail_filter(
        normal_seconds=normal_seconds,
        slow_tail_output_seconds=slow_tail_output_seconds,
        tail_source_seconds=tail_source_seconds,
    )
    return [
        ffmpeg_binary,
        "-y",
        "-i",
        str(input_path),
        "-filter_complex",
        filter_graph,
        "-map",
        "[outv]",
        "-an",
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-movflags",
        "+faststart",
        str(output_path),
    ]


def derive_slow_tail_clip(
    *,
    input_path: str | Path,
    output_path: str | Path,
    normal_seconds: float,
    slow_tail_output_seconds: float,
    tail_source_seconds: float,
    ffmpeg_binary: str | None = None,
) -> dict[str, float | str]:
    """Create a derived clip with a slowed final beat."""
    source = Path(input_path)
    if not source.is_file():
        raise FileNotFoundError(f"Input clip not found: {source}")

    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    ffmpeg = resolve_ffmpeg_binary(ffmpeg_binary)
    command = build_slow_tail_command(
        ffmpeg_binary=ffmpeg,
        input_path=source,
        output_path=target,
        normal_seconds=normal_seconds,
        slow_tail_output_seconds=slow_tail_output_seconds,
        tail_source_seconds=tail_source_seconds,
    )
    subprocess.run(command, check=True, capture_output=True, text=True)
    return {
        "input_path": str(source),
        "output_path": str(target),
        "normal_seconds": float(normal_seconds),
        "slow_tail_output_seconds": float(slow_tail_output_seconds),
        "tail_source_seconds": float(tail_source_seconds),
        "target_duration_seconds": float(normal_seconds + slow_tail_output_seconds),
        "ffmpeg_binary": ffmpeg,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Post-process Kling clips into delivery variants.")
    parser.add_argument("--input", required=True, type=Path, help="Source MP4 path")
    parser.add_argument("--output", required=True, type=Path, help="Derived MP4 path")
    parser.add_argument(
        "--normal-seconds",
        type=float,
        required=True,
        help="Initial segment duration to keep at normal speed",
    )
    parser.add_argument(
        "--slow-tail-output-seconds",
        type=float,
        required=True,
        help="Duration of the slowed output tail",
    )
    parser.add_argument(
        "--tail-source-seconds",
        type=float,
        required=True,
        help="Amount of source footage to stretch into the slowed tail",
    )
    parser.add_argument("--ffmpeg-binary", default=None, help="Explicit ffmpeg executable path")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = derive_slow_tail_clip(
            input_path=args.input,
            output_path=args.output,
            normal_seconds=args.normal_seconds,
            slow_tail_output_seconds=args.slow_tail_output_seconds,
            tail_source_seconds=args.tail_source_seconds,
            ffmpeg_binary=args.ffmpeg_binary,
        )
        print(json.dumps(result, indent=2))
        return 0
    except Exception as exc:  # pragma: no cover - CLI failure path
        print(json.dumps({"status": "error", "error": str(exc)}, indent=2))
        return 1


if __name__ == "__main__":  # pragma: no cover - CLI entry
    raise SystemExit(main())
