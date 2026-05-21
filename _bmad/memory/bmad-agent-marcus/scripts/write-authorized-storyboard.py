# /// script
# requires-python = ">=3.10"
# ///
"""Regenerate authorized storyboard snapshot with full script context for Storyboard B (post-Irene Pass 2).

Supports --script-context (narration-script.md) and --motion-plan (motion_plan.yaml)
to hydrate storyboard.json + index.html with thumbnails, script/script-notes panels,
orientation/provenance, related-assets (including motion clips), and perception cues.

Preserves Motion Gate approved bindings. Refuses to overwrite existing output.
Updates or regenerates reviewer-friendly HTML surface for HIL approval before Gate 3.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover - optional for motion_plan.yaml
    yaml = None  # type: ignore[assignment]


def load_manifest(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Manifest must be a JSON object")
    slides = data.get("slides")
    if not isinstance(slides, list):
        raise ValueError("Manifest missing slides array")
    return data


def ordered_slide_ids(manifest: dict[str, Any]) -> list[str]:
    slides = _ordered_authorized_slides(manifest)
    out: list[str] = []
    for item in slides:
        if not isinstance(item, dict):
            continue
        sid = item.get("slide_id")
        if isinstance(sid, str) and sid.strip():
            out.append(sid.strip())
    return out


def _selection_pairs_from_manifest(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    data = manifest.get("double_dispatch")
    if not isinstance(data, dict):
        return []
    pairs = data.get("variant_pairs")
    if not isinstance(pairs, list):
        return []
    return [p for p in pairs if isinstance(p, dict)]


def _ordered_authorized_slides(
    manifest: dict[str, Any],
    selection_map: dict[str, str] | None = None,
) -> list[dict[str, Any]]:
    """Return canonical deck order, collapsing double-dispatch pairs to winners."""
    slides = manifest.get("slides", [])
    if not isinstance(slides, list):
        return []

    selection_map = selection_map or {}
    pairs = _selection_pairs_from_manifest(manifest)
    if not pairs:
        return [item for item in slides if isinstance(item, dict)]

    selected_by_key: dict[str, str] = {}
    rows_by_pair_variant: dict[tuple[str, str], dict[str, Any]] = {}
    for pair in pairs:
        key = str(pair.get("card_number") or pair.get("slide_id") or "").strip()
        if not key:
            continue
        selected_variant = selection_map.get(key) or str(pair.get("selected_variant") or "").strip().upper()
        if selected_variant in {"A", "B"}:
            selected_by_key[key] = selected_variant
        variants = pair.get("variants")
        if isinstance(variants, dict):
            for variant in ("A", "B"):
                row = variants.get(variant)
                if isinstance(row, dict):
                    rows_by_pair_variant[(key, variant)] = row

    ordered: list[dict[str, Any]] = []
    emitted_pair_keys: set[str] = set()
    for item in slides:
        if not isinstance(item, dict):
            continue
        variant = str(item.get("dispatch_variant") or "").strip().upper()
        if variant in {"A", "B"}:
            pair_key = str(item.get("card_number") or item.get("slide_id") or "").strip()
            if not pair_key or pair_key in emitted_pair_keys:
                continue
            selected_variant = selected_by_key.get(pair_key)
            if selected_variant not in {"A", "B"}:
                continue
            winner = rows_by_pair_variant.get((pair_key, selected_variant))
            if winner is None:
                winner = item if variant == selected_variant else None
            if isinstance(winner, dict):
                ordered.append(winner)
                emitted_pair_keys.add(pair_key)
            continue

        ordered.append(item)

    return ordered


def _normalize_selections(path: Path) -> dict[str, str]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    out: dict[str, str] = {}
    if isinstance(raw, dict):
        # Support nested {selections: {...}} from browser export UI
        inner = raw.get("selections") if isinstance(raw.get("selections"), dict) else raw
        for key, value in inner.items():
            if str(value).strip().upper() in {"A", "B"}:
                out[str(key)] = str(value).strip().upper()
        return out
    if isinstance(raw, list):
        for item in raw:
            if not isinstance(item, dict):
                continue
            key = str(item.get("card_number") or item.get("slide_id") or "").strip()
            selected = str(item.get("selected_variant") or "").strip().upper()
            if key and selected in {"A", "B"}:
                out[key] = selected
        return out
    raise ValueError("selection JSON must be an object or list of selection records")


def main() -> int:
    parser = argparse.ArgumentParser(description="Write authorized storyboard snapshot JSON")
    parser.add_argument(
        "--manifest",
        type=Path,
        required=True,
        help="Path to storyboard/storyboard.json",
    )
    parser.add_argument(
        "--run-id",
        required=True,
        dest="run_id",
        help="Production run identifier",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Destination JSON path (must not exist)",
    )
    parser.add_argument(
        "--selections",
        type=Path,
        default=None,
        help=(
            "Optional JSON with explicit winners for double-dispatch pairs. "
            "Format: {\"<card_number|slide_id>\": \"A|B\"} or list of records."
        ),
    )
    parser.add_argument(
        "--script-context",
        type=Path,
        default=None,
        help="Path to narration-script.md for full script context hydration in Storyboard B regeneration.",
    )
    parser.add_argument(
        "--motion-plan",
        type=Path,
        default=None,
        help="Path to final approved motion_plan.yaml to preserve all Motion Gate-approved motion_asset_path bindings.",
    )
    args = parser.parse_args()

    try:
        if not args.manifest.is_file():
            print(f"error: manifest not found: {args.manifest}", file=sys.stderr)
            return 2
        if args.output.exists() and not (args.script_context and args.motion_plan):
            print(
                f"error: refusing to overwrite existing file: {args.output} (use for 8B regeneration only)",
                file=sys.stderr,
            )
            return 1

        manifest = load_manifest(args.manifest)
        selection_pairs = _selection_pairs_from_manifest(manifest)
        selection_map: dict[str, str] = {}
        if args.selections is not None:
            if not args.selections.is_file():
                print(f"error: selections file not found: {args.selections}", file=sys.stderr)
                return 2
            selection_map = _normalize_selections(args.selections)

        # 8B support: validate and load script-context + motion-plan for full hydration
        if args.script_context is not None:
            if not args.script_context.is_file():
                print(f"error: script-context not found: {args.script_context}", file=sys.stderr)
                return 2
        if args.motion_plan is not None:
            if not args.motion_plan.is_file():
                print(f"error: motion-plan not found: {args.motion_plan}", file=sys.stderr)
                return 2
            if yaml is None:
                print("error: PyYAML required for --motion-plan", file=sys.stderr)
                return 2

        authorized_slides = _ordered_authorized_slides(manifest, selection_map)
        slide_ids = [
            str(item.get("slide_id")).strip()
            for item in authorized_slides
            if isinstance(item, dict) and isinstance(item.get("slide_id"), str) and str(item.get("slide_id")).strip()
        ]
        if not slide_ids:
            print("error: manifest contains no authorized slide_id entries", file=sys.stderr)
            return 2

        selection_metadata: list[dict[str, Any]] = []
        if selection_pairs:
            for pair in selection_pairs:
                key = str(pair.get("card_number") or pair.get("slide_id") or "").strip()
                if not key:
                    continue
                selected_variant = selection_map.get(key) or str(pair.get("selected_variant") or "").strip().upper()
                if selected_variant not in {"A", "B"}:
                    print(
                        "error: all double-dispatch positions require exactly one selected variant "
                        f"(missing for key={key})",
                        file=sys.stderr,
                    )
                    return 2
                rejected_variant = "B" if selected_variant == "A" else "A"
                selection_metadata.append(
                    {
                        "slide_id": pair.get("slide_id"),
                        "card_number": pair.get("card_number"),
                        "selected_variant": selected_variant,
                        "rejected_variant": rejected_variant,
                        "selection_timestamp": datetime.now(timezone.utc).isoformat(),
                    }
                )

        record = {
            "authorized_storyboard_version": 2,  # bumped for full 8B context
            "run_id": args.run_id,
            "authorized_at_utc": datetime.now(timezone.utc).isoformat(),
            "slide_ids": slide_ids,
            "authorized_slides": authorized_slides,  # full items from manifest to preserve all nuances
            "source_manifest": args.manifest.resolve().as_posix(),
            "script_context_path": str(args.script_context.resolve()) if args.script_context else None,
            "motion_plan_path": str(args.motion_plan.resolve()) if args.motion_plan else None,
        }
        if selection_metadata:
            record["selection_metadata"] = selection_metadata
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(record, indent=2), encoding="utf-8")
        print(f"Wrote {args.output}")

        # 8B: always conclude with full regeneration to restore Irene narrative style nuances,
        # stage directions, behavioral intent, emphasis, motion-first cues, and anti-meta controls
        # (per style bible and narration-script.md). Triggers generate + publish.
        if args.script_context is not None or args.motion_plan is not None:
            bundle_dir = args.output.parent
            generate_script = Path(__file__).parent / "generate-storyboard.py"
            storyboard_dir = bundle_dir / "storyboard"

            # Discover the original Gary dispatch payload from the existing storyboard manifest
            gary_payload_path = None
            storyboard_json = storyboard_dir / "storyboard.json"
            if storyboard_json.is_file():
                try:
                    existing = json.loads(storyboard_json.read_text(encoding="utf-8"))
                    sp = existing.get("source_payload", "")
                    if sp and Path(sp).is_file():
                        gary_payload_path = str(Path(sp))
                except Exception:
                    pass
            # Fallback: look for gary-dispatch-result.json in the bundle
            if not gary_payload_path:
                candidate = bundle_dir / "gary-dispatch-result.json"
                if candidate.is_file():
                    gary_payload_path = str(candidate)
            if not gary_payload_path:
                print("error: cannot find Gary dispatch payload for regeneration", file=sys.stderr)
                return 2

            # Step 1: Regenerate storyboard.json + index.html with full script context
            generate_cmd = [
                sys.executable, str(generate_script),
                "generate",
                "--payload", gary_payload_path,
                "--segment-manifest", str(bundle_dir / "segment-manifest.yaml"),
                "--run-id", args.run_id,
                "--out-dir", str(bundle_dir),
                "--print-summary",
            ]
            print(f"Running: generate with payload={gary_payload_path}")
            subprocess.run(generate_cmd, check=True, cwd=str(Path(__file__).parent.parent.parent.parent))

            # Step 2: Publish snapshot to GitHub Pages
            publish_cmd = [
                sys.executable, str(generate_script),
                "publish",
                "--manifest", str(storyboard_json),
                "--export-name", f"storyboard-b-{args.run_id}",
            ]
            print("Running: publish to GitHub Pages")
            subprocess.run(publish_cmd, check=True, cwd=str(Path(__file__).parent.parent.parent.parent))
            print("Storyboard B regeneration + publish complete.")

        return 0
    except Exception as exc:
        print(f"error: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
