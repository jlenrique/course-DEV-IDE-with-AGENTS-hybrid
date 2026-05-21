# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

# ruff: noqa: E501

"""Generate a Descript Assembly Guide from a completed manifest."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path
from typing import Any

import yaml

_VIDEO_SUFFIXES = {".mp4", ".webm", ".mov", ".m4v"}


def load_manifest(manifest_path: str | Path) -> dict[str, Any]:
    """Load a manifest from disk."""
    manifest_path = Path(manifest_path)
    return yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}


def find_repo_root(start: Path) -> Path:
    """Walk parents from ``start`` until a directory containing ``.git`` is found."""
    current = start.resolve()
    for candidate in [current, *current.parents]:
        if (candidate / ".git").exists():
            return candidate
    raise FileNotFoundError(
        "Could not locate repository root (no .git directory in parents of "
        f"{start}). Pass repo_root explicitly if working outside a git clone."
    )


def _sanitize_cluster_token(value: Any) -> str:
    token = "".join(ch if str(ch).isalnum() else "_" for ch in str(value or "").strip())
    token = "_".join(part for part in token.split("_") if part)
    return token or "unknown"


def _count_words(text: str | None) -> int:
    tokens = [token for token in str(text or "").replace("\n", " ").split(" ") if token]
    return len(tokens)


def _clip_text(text: str | None, *, max_chars: int = 180) -> str | None:
    cleaned = " ".join(str(text or "").split()).strip()
    if not cleaned:
        return None
    if len(cleaned) <= max_chars:
        return cleaned
    return f"{cleaned[: max_chars - 3].rstrip()}..."


def _transition_annotation(transition_scope: str) -> str:
    if transition_scope == "within-cluster":
        return "[TRANSITION: cut — no effect]"
    if transition_scope == "cluster-boundary":
        return "[TRANSITION: beat/pause — brief black or fade]"
    return "[TRANSITION: manifest-default treatment]"


def _pacing_guidance(transition_scope: str, bridge_type: str) -> str:
    if transition_scope == "within-cluster":
        return "maintain tight pacing — no pauses between slides"
    if bridge_type == "cluster_boundary":
        return "bridge audio covers the transition — no additional pause needed"
    if transition_scope == "cluster-boundary":
        return "insert 0.5-1.0s beat between clusters for cognitive reset"
    return "maintain standard pacing for standalone flow"


def sync_approved_visuals_to_assembly_bundle(
    manifest_path: str | Path,
    *,
    visuals_subdir: str = "visuals",
    motion_subdir: str = "motion",
    repo_root: str | Path | None = None,
) -> dict[str, Any]:
    """Copy segment ``visual_file`` assets next to the manifest and rewrite paths.

    Approved slides often live under a Gary/Gamma export tree. For a completed
    assembly bundle (audio, captions, guide, summaries), copy those stills into
    ``<manifest_dir>/<visuals_subdir>/`` and update each segment's ``visual_file``
    to the new repo-relative path so Descript and reviewers use one folder.
    """
    manifest_path = Path(manifest_path).resolve()
    root = Path(repo_root).resolve() if repo_root else find_repo_root(manifest_path)
    manifest = load_manifest(manifest_path)
    segments = manifest.get("segments", [])
    if not segments:
        raise ValueError("Manifest has no segments.")

    dest_dir = (manifest_path.parent / visuals_subdir).resolve()
    dest_dir.mkdir(parents=True, exist_ok=True)

    copies: list[dict[str, str]] = []
    motion_copies: list[dict[str, str]] = []
    for segment in segments:
        rel_visual = segment.get("visual_file")
        if not rel_visual:
            raise ValueError(f"Segment {segment.get('id', '<unknown>')} missing visual_file.")
        src = (root / rel_visual).resolve()
        if not src.is_file():
            raise FileNotFoundError(f"Visual not found for {segment.get('id')}: {src}")

        cluster_id = str(segment.get("cluster_id") or "").strip()
        if cluster_id:
            cluster_dir = dest_dir / f"cluster_{_sanitize_cluster_token(cluster_id)}"
            cluster_dir.mkdir(parents=True, exist_ok=True)
            dest_file = cluster_dir / src.name
        else:
            dest_file = dest_dir / src.name
        if (
            dest_file.exists()
            and dest_file.resolve() != src.resolve()
            and dest_file.read_bytes() != src.read_bytes()
        ):
            raise ValueError(
                "Refusing visual overwrite collision for "
                f"segment {segment.get('id', '<unknown>')}: {dest_file}"
            )
        if dest_file.resolve() != src.resolve():
            shutil.copy2(src, dest_file)

        new_rel = (dest_file.relative_to(root)).as_posix()
        if rel_visual != new_rel:
            copies.append({"segment": segment["id"], "from": rel_visual, "to": new_rel})

        motion_path = segment.get("motion_asset_path")
        motion_type = str(segment.get("motion_type") or "static").strip().lower()
        if motion_type != "static" or motion_path:
            if not motion_path:
                raise ValueError(
                    f"Segment {segment.get('id', '<unknown>')} missing motion_asset_path."
                )
            src_motion = (root / str(motion_path)).resolve()
            if not src_motion.is_file():
                raise FileNotFoundError(
                    f"Motion asset not found for {segment.get('id')}: {src_motion}"
                )
            motion_dir = (manifest_path.parent / motion_subdir).resolve()
            motion_dir.mkdir(parents=True, exist_ok=True)
            if cluster_id:
                cluster_motion_dir = motion_dir / f"cluster_{_sanitize_cluster_token(cluster_id)}"
                cluster_motion_dir.mkdir(parents=True, exist_ok=True)
                dest_motion = cluster_motion_dir / src_motion.name
            else:
                dest_motion = motion_dir / src_motion.name
            if (
                dest_motion.exists()
                and dest_motion.resolve() != src_motion.resolve()
                and dest_motion.read_bytes() != src_motion.read_bytes()
            ):
                raise ValueError(
                    "Refusing motion overwrite collision for "
                    f"segment {segment.get('id', '<unknown>')}: {dest_motion}"
                )
            if dest_motion.resolve() != src_motion.resolve():
                shutil.copy2(src_motion, dest_motion)
            new_motion_rel = (dest_motion.relative_to(root)).as_posix()
            if motion_path != new_motion_rel:
                motion_copies.append(
                    {"segment": segment["id"], "from": str(motion_path), "to": new_motion_rel}
                )

    text = manifest_path.read_text(encoding="utf-8")
    for item in copies:
        old, new = item["from"], item["to"]
        occurrences = text.count(old)
        if occurrences != 1:
            raise ValueError(
                "Refusing manifest edit: path "
                f"{old!r} appears {occurrences} times in {manifest_path} (expected 1)."
            )
        text = text.replace(old, new)
    for item in motion_copies:
        old, new = item["from"], item["to"]
        occurrences = text.count(old)
        if occurrences != 1:
            raise ValueError(
                "Refusing manifest edit: path "
                f"{old!r} appears {occurrences} times in {manifest_path} (expected 1)."
            )
        text = text.replace(old, new)
    if copies or motion_copies:
        manifest_path.write_text(text, encoding="utf-8")

    return {
        "manifest_path": str(manifest_path),
        "visuals_dir": str(dest_dir),
        "copies": copies,
        "motion_dir": str((manifest_path.parent / motion_subdir).resolve()),
        "motion_copies": motion_copies,
    }


def save_markdown(content: str, output_path: str | Path) -> Path:
    """Write the generated guide to disk."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
    return output_path


def format_timestamp(seconds: float) -> str:
    """Format seconds as HH:MM:SS.mmm."""
    total_ms = round(seconds * 1000)
    hours, remainder = divmod(total_ms, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    secs, milliseconds = divmod(remainder, 1000)
    return f"{hours:02}:{minutes:02}:{secs:02}.{milliseconds:03}"


def behavioral_note(intent: str | None) -> str:
    """Convert behavioral intent into a practical composition note."""
    notes = {
        "credible": "Keep the pacing restrained and the visual treatment clean and authoritative.",
        "alarming": "Preserve tension through sharper emphasis and avoid softening the transition impact.",
        "moving": "Allow emotional breathing room with slightly longer holds and gentle transitions.",
        "attention-reset": "Use this beat to simplify the frame and reset learner focus before the next idea.",
        "reflective": "Favor quiet pacing and avoid clutter that would break reflective attention.",
        "provocative": "Let the cut and emphasis create productive friction without feeling sensationalized.",
        "urgent": "Keep momentum tight and avoid dead air or overly decorative holds.",
        "clear-guidance": "Optimize for clarity and confidence; avoid unnecessary dramatic treatment.",
        "attention-grabbing": "Open strong and clean so the learner's focus is captured immediately.",
    }
    if not intent:
        return "Preserve the approved instructional tone without adding unnecessary dramatic treatment."
    return notes.get(
        intent,
        f"Preserve the intended `{intent}` effect consistently through pacing, transitions, and emphasis.",
    )


def validate_manifest(manifest: dict[str, Any]) -> None:
    """Fail fast when the manifest is not ready for composition."""
    segments = manifest.get("segments", [])
    if not segments:
        raise ValueError("Manifest has no segments.")
    for segment in segments:
        missing = [
            field
            for field in ("id", "narration_duration", "narration_file", "visual_file")
            if not segment.get(field)
        ]
        if missing:
            raise ValueError(
                f"Segment {segment.get('id', '<unknown>')} missing required fields: {', '.join(missing)}"
            )
        motion_type = str(segment.get("motion_type") or "static").strip().lower() or "static"
        if motion_type != "static":
            if not segment.get("motion_asset_path"):
                raise ValueError(
                    f"Segment {segment.get('id', '<unknown>')} missing required fields: motion_asset_path"
                )
            if not segment.get("motion_duration_seconds"):
                raise ValueError(
                    f"Segment {segment.get('id', '<unknown>')} missing required fields: motion_duration_seconds"
                )
            visual_file = str(segment.get("visual_file") or "").strip()
            if Path(visual_file).suffix.lower() in _VIDEO_SUFFIXES:
                raise ValueError(
                    f"Segment {segment.get('id', '<unknown>')} must keep visual_file as the approved still reference; motion clips belong in motion_asset_path"
                )


def build_timeline_rows(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    """Build ordered timeline rows with cumulative start times."""
    segments = manifest.get("segments", [])
    cluster_interstitial_totals: dict[str, int] = {}
    cluster_topics: dict[str, str] = {}
    cluster_master_intents: dict[str, str] = {}
    for segment in segments:
        cluster_id = str(segment.get("cluster_id") or "").strip()
        if not cluster_id:
            continue
        cluster_role = str(segment.get("cluster_role") or "").strip().lower()
        if cluster_role == "interstitial":
            cluster_interstitial_totals[cluster_id] = (
                cluster_interstitial_totals.get(cluster_id, 0) + 1
            )
        cluster_topic = str(
            segment.get("cluster_topic") or segment.get("narrative_arc") or ""
        ).strip()
        if cluster_topic and cluster_id not in cluster_topics:
            cluster_topics[cluster_id] = cluster_topic
        master_behavioral_intent = str(segment.get("master_behavioral_intent") or "").strip()
        if master_behavioral_intent and cluster_id not in cluster_master_intents:
            cluster_master_intents[cluster_id] = master_behavioral_intent

    current_start = 0.0
    rows: list[dict[str, Any]] = []
    cluster_interstitial_seen: dict[str, int] = {}
    previous_cluster_id: str | None = None
    for segment in segments:
        narration_duration = float(segment["narration_duration"])
        visual_duration = (
            float(segment["visual_duration"])
            if segment.get("visual_duration") is not None
            else narration_duration
        )
        cluster_id_raw = str(segment.get("cluster_id") or "").strip()
        cluster_id = cluster_id_raw or None
        cluster_role = str(segment.get("cluster_role") or "none").strip().lower() or "none"
        if not rows:
            transition_scope = "start"
        elif previous_cluster_id and cluster_id and previous_cluster_id == cluster_id:
            transition_scope = "within-cluster"
        elif previous_cluster_id is None and cluster_id is None:
            transition_scope = "flat"
        else:
            transition_scope = "cluster-boundary"

        interstitial_position = None
        interstitial_total = None
        if cluster_id and cluster_role == "interstitial":
            interstitial_position = cluster_interstitial_seen.get(cluster_id, 0) + 1
            cluster_interstitial_seen[cluster_id] = interstitial_position
            interstitial_total = cluster_interstitial_totals.get(cluster_id, interstitial_position)

        cluster_topic = cluster_topics.get(cluster_id or "")
        if cluster_id and cluster_role == "head":
            topic = cluster_topic or "cluster topic"
            cluster_label = f"[HEAD — Cluster {cluster_id}: \"{topic}\"]"
        elif cluster_id and cluster_role == "interstitial":
            interstitial_type = str(segment.get("interstitial_type") or "interstitial").strip()
            isolation_target = str(segment.get("isolation_target") or "focus").strip()
            cluster_label = (
                f"[INTERSTITIAL {interstitial_position}/{interstitial_total} — "
                f"{interstitial_type}: \"{isolation_target}\"]"
            )
        else:
            cluster_label = "[STANDALONE]"

        motion_type = str(segment.get("motion_type") or "static").strip().lower() or "static"
        motion_duration = (
            float(segment["motion_duration_seconds"])
            if motion_type != "static" and segment.get("motion_duration_seconds") is not None
            else None
        )
        segment_duration = max(narration_duration, motion_duration or 0.0)

        narration_text = str(segment.get("narration_text") or "")
        word_count = _count_words(narration_text)
        expected_audio_seconds = round((word_count * 60.0) / 150.0, 1) if word_count else None

        bridge_type = (
            str(segment.get("bridge_type") or "none").strip().lower() or "none"
        )
        if cluster_role == "interstitial":
            audio_note = "[AUDIO: VO segment, 10-16s]"
        elif cluster_role == "head":
            audio_note = "[AUDIO: VO segment, 32-56s]"
        else:
            audio_note = "[AUDIO: VO segment]"
        boundary_audio_note = (
            "[AUDIO: bridge VO, 15-20s]" if bridge_type == "cluster_boundary" else None
        )

        transition_annotation = _transition_annotation(transition_scope)
        pacing_guidance = _pacing_guidance(transition_scope, bridge_type)
        bridge_text = (
            _clip_text(segment.get("narration_text"))
            if bridge_type == "cluster_boundary"
            else None
        )

        master_behavioral_intent = str(
            segment.get("master_behavioral_intent")
            or cluster_master_intents.get(cluster_id or "")
            or "none"
        ).strip() or "none"

        rows.append(
            {
                "id": segment["id"],
                "start": current_start,
                "segment_duration": segment_duration,
                "narration_duration": narration_duration,
                "visual_duration": visual_duration,
                "transition_in": segment.get("transition_in", "none"),
                "transition_out": segment.get("transition_out", "none"),
                "behavioral_intent": segment.get("behavioral_intent"),
                "narration_file": segment["narration_file"],
                "visual_file": segment["visual_file"],
                "sfx_file": segment.get("sfx_file"),
                "music": segment.get("music"),
                "visual_mode": segment.get("visual_mode"),
                "motion_type": motion_type,
                "motion_asset_path": segment.get("motion_asset_path"),
                "motion_duration_seconds": motion_duration,
                "bridge_type": bridge_type,
                "cluster_id": cluster_id,
                "cluster_role": cluster_role,
                "cluster_position": segment.get("cluster_position") or "none",
                "cluster_topic": cluster_topic or "",
                "master_behavioral_intent": master_behavioral_intent,
                "interstitial_type": segment.get("interstitial_type") or "",
                "isolation_target": segment.get("isolation_target") or "",
                "cluster_label": cluster_label,
                "transition_scope": transition_scope,
                "transition_annotation": transition_annotation,
                "audio_note": audio_note,
                "boundary_audio_note": boundary_audio_note,
                "pacing_guidance": pacing_guidance,
                "word_count": word_count,
                "expected_audio_seconds": expected_audio_seconds,
                "bridge_text": bridge_text,
            }
        )
        previous_cluster_id = cluster_id
        current_start += segment_duration
    return rows


def generate_assembly_guide(manifest: dict[str, Any], manifest_path: str | Path) -> str:
    """Generate the human-readable Descript Assembly Guide."""
    validate_manifest(manifest)
    rows = build_timeline_rows(manifest)
    total_runtime = rows[-1]["start"] + rows[-1]["narration_duration"]
    lesson_id = manifest.get("lesson_id", "lesson")
    title = manifest.get("title", lesson_id)

    lines = [
        f"# Descript Assembly Guide — {title}",
        "",
        "## Summary",
        "",
        f"- Lesson ID: `{lesson_id}`",
        f"- Manifest: `{manifest_path}`",
        f"- Total runtime: `{format_timestamp(total_runtime)}`",
        "- Track plan: `V1` visuals, `A1` narration, `A2` music, `A3` SFX",
        "",
    ]

    clusters: dict[str, list[dict[str, Any]]] = {}
    cluster_order: list[str] = []
    for row in rows:
        cluster_id = row.get("cluster_id")
        if not cluster_id:
            continue
        if cluster_id not in clusters:
            clusters[cluster_id] = []
            cluster_order.append(cluster_id)
        clusters[cluster_id].append(row)

    if cluster_order:
        lines.extend(["## Cluster Overview", ""])
        for cluster_id in cluster_order:
            cluster_rows = clusters[cluster_id]
            head = next(
                (row for row in cluster_rows if row.get("cluster_role") == "head"),
                cluster_rows[0],
            )
            topic = head.get("cluster_topic") or "cluster topic"
            master_behavioral_intent = head.get("master_behavioral_intent") or "none"
            interstitial_count = sum(
                1 for row in cluster_rows if row.get("cluster_role") == "interstitial"
            )
            lines.extend(
                [
                    f"### Cluster {cluster_id}",
                    f"- Header: `[HEAD — Cluster {cluster_id}: \"{topic}\"]`",
                    f"- Master behavioral intent: `{master_behavioral_intent}`",
                    f"- Interstitial count: `{interstitial_count}`",
                    "- Within-cluster pacing: maintain tight pacing — no pauses between slides",
                    "- Between-cluster pacing: insert 0.5-1.0s beat between clusters for cognitive reset",
                    "",
                ]
            )

    lines.extend(
        [
            "## Asset Inventory",
            "",
            "| Asset | Track | Segment | Path |",
            "|-------|-------|---------|------|",
        ]
    )
    for row in rows:
        lines.append(f"| Narration | A1 | `{row['id']}` | `{row['narration_file']}` |")
        lines.append(f"| Visual | V1 | `{row['id']}` | `{row['visual_file']}` |")
        if row.get("motion_type") != "static" and row.get("motion_asset_path"):
            lines.append(f"| Motion | V1 | `{row['id']}` | `{row['motion_asset_path']}` |")
        if row.get("sfx_file"):
            lines.append(f"| SFX | A3 | `{row['id']}` | `{row['sfx_file']}` |")
    lines.extend(
        [
            "",
            "## Timeline Table",
            "",
            "| Segment | Start | Label | Narration | Visual | Transition Annotation | Audio Note | Bridge / Cluster | Behavioral Intent |",
            "|---------|-------|-------|-----------|--------|-----------------------|------------|------------------|-------------------|",
        ]
    )
    for row in rows:
        transitions = row.get("transition_annotation") or "[TRANSITION: manifest-default treatment]"
        bridge_cluster = (
            f"{row.get('bridge_type') or 'none'} / "
            f"{row.get('cluster_id') or 'standalone'}"
        )
        lines.append(
            f"| `{row['id']}` | `{format_timestamp(row['start'])}` | "
            f"`{row.get('cluster_label')}` | `{row['narration_duration']:.2f}s` | `{row['visual_duration']:.2f}s` | "
            f"`{transitions}` | `{row.get('audio_note')}` | `{bridge_cluster}` | `{row.get('behavioral_intent') or 'none'}` |"
        )

    lines.extend(["", "## Segment-by-Segment Assembly Instructions", ""])
    for row in rows:
        lines.extend(
            [
                f"### {row['id']}",
                f"- Start at `{format_timestamp(row['start'])}`",
                f"- Place `{row['narration_file']}` on `A1`",
                f"- Set segment duration to `{row['segment_duration']:.2f}s`",
                f"- Segment label: `{row.get('cluster_label')}`",
                f"- Transition in/out: `{row['transition_in']}` / `{row['transition_out']}`",
                f"- Transition annotation: `{row.get('transition_annotation')}`",
                f"- Bridge type: `{row.get('bridge_type') or 'none'}`",
                f"- Cluster context: `{row.get('cluster_id') or 'standalone'} / {row.get('cluster_role') or 'none'} / {row.get('cluster_position') or 'none'}`",
                f"- Master behavioral intent: `{row.get('master_behavioral_intent') or 'none'}`",
                f"- Audio treatment: `{row.get('audio_note')}`",
                f"- Behavioral intent: `{row.get('behavioral_intent') or 'none'}`",
                f"- Intent note: {behavioral_note(row.get('behavioral_intent'))}",
                f"- Pacing guidance: {row.get('pacing_guidance')}",
            ]
        )
        if row.get("expected_audio_seconds") is not None:
            lines.append(
                f"- Audio estimate at 150 WPM: `{row.get('expected_audio_seconds'):.1f}s` (`{row.get('word_count')}` words)."
            )
        if row.get("boundary_audio_note"):
            lines.append(f"- Boundary audio treatment: `{row.get('boundary_audio_note')}`")
        if row.get("bridge_text"):
            lines.append(
                f"- Bridge text (synthesis + forward pull): "
                f"`{row.get('bridge_text')}`"
            )
        if row.get("motion_type") != "static" and row.get("motion_asset_path"):
            lines.append(
                f"- Play `{row['motion_asset_path']}` on the video track for `{float(row['motion_duration_seconds']):.2f}s`, aligned to narration segment `{row['id']}`."
            )
            lines.append(
                f"- Keep `{row['visual_file']}` available as the approved still reference/poster frame if needed."
            )
        else:
            lines.append(f"- Place `{row['visual_file']}` on `V1`")
        if row["visual_mode"] == "static-hold":
            lines.append("- Hold the still visual for the full narration duration.")
        elif row["visual_duration"] != row["narration_duration"]:
            lines.append(
                f"- Adjust or hold the visual so it lands cleanly against the `{row['narration_duration']:.2f}s` narration."
            )
        if row.get("music"):
            lines.append(f"- Music cue: `{row['music']}` on `A2`.")
        if row.get("sfx_file"):
            lines.append(f"- Add `{row['sfx_file']}` on `A3` at the segment start or cue point.")
        lines.append("")

    lines.extend(
        [
            "## Final Check",
            "",
            "- Verify every narration clip starts at the listed timestamp.",
            "- Confirm visual pacing supports the segment's behavioral intent.",
            "- Confirm caption export matches the ElevenLabs VTT timing.",
            "- Export final MP4 + VTT for Quinn-R post-composition review.",
            "",
        ]
    )
    return "\n".join(lines)


def generate_assembly_guide_file(
    manifest_path: str | Path,
    output_path: str | Path,
) -> Path:
    """Generate and save a Descript Assembly Guide from a manifest path."""
    manifest = load_manifest(manifest_path)
    content = generate_assembly_guide(manifest, manifest_path)
    return save_markdown(content, output_path)


def build_parser() -> argparse.ArgumentParser:
    """Build CLI parser (subcommands + legacy two-arg guide mode)."""
    parser = argparse.ArgumentParser(
        description="Compositor: sync approved visuals into the assembly bundle and/or "
        "generate a Descript Assembly Guide."
    )
    sub = parser.add_subparsers(dest="command")

    guide = sub.add_parser("guide", help="Generate Descript Assembly Guide markdown.")
    guide.add_argument("manifest_path")
    guide.add_argument("output_path")

    sync = sub.add_parser(
        "sync-visuals",
        help="Copy approved visual_file assets next to the manifest; update manifest paths.",
    )
    sync.add_argument("manifest_path")
    sync.add_argument(
        "--subdir",
        default="visuals",
        help="Folder under the manifest directory for copied stills (default: visuals).",
    )
    sync.add_argument(
        "--repo-root",
        default=None,
        help="Repository root (defaults to parent chain containing .git).",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    raw = list(sys.argv[1:] if argv is None else argv)
    if len(raw) >= 2 and raw[0] not in ("guide", "sync-visuals", "--help", "-h"):
        raw = ["guide", *raw]

    args = build_parser().parse_args(raw)
    try:
        if getattr(args, "command", None) is None:
            build_parser().print_help()
            return 2
        if args.command == "sync-visuals":
            summary = sync_approved_visuals_to_assembly_bundle(
                args.manifest_path,
                visuals_subdir=args.subdir,
                repo_root=args.repo_root,
            )
            print(yaml.dump(summary, default_flow_style=False, sort_keys=False).strip())
            return 0
        if args.command == "guide":
            output = generate_assembly_guide_file(args.manifest_path, args.output_path)
            print(str(output))
            return 0
        build_parser().print_help()
        return 2
    except Exception as exc:  # pragma: no cover
        print(f"ERROR: {exc}")
        return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
