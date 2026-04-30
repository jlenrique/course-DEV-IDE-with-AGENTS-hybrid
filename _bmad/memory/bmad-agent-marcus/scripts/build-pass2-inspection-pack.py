# /// script
# requires-python = ">=3.10"
# ///
"""Build reviewer-facing slide and motion inspection artifacts for Prompt 8."""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover - optional for yaml input
    yaml = None  # type: ignore[assignment]

from PIL import Image, ImageDraw

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from skills.sensory_bridges.scripts.video_to_agent import _extract_keyframes  # noqa: E402
except ModuleNotFoundError:  # pragma: no cover - direct file import fallback
    scripts_dir = PROJECT_ROOT / "skills" / "sensory-bridges" / "scripts"

    def _load_bridge_module(name: str, filename: str):
        if name in sys.modules:
            return sys.modules[name]
        spec = importlib.util.spec_from_file_location(name, scripts_dir / filename)
        if spec is None or spec.loader is None:
            raise ModuleNotFoundError(f"Unable to load {name} from {filename}")
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        return module

    bridge_utils = _load_bridge_module(
        "skills.sensory_bridges.scripts.bridge_utils",
        "bridge_utils.py",
    )
    sys.modules.setdefault("skills", type(sys)("skills"))
    sys.modules.setdefault("skills.sensory_bridges", type(sys)("skills.sensory_bridges"))
    sys.modules.setdefault("skills.sensory_bridges.scripts", type(sys)("skills.sensory_bridges.scripts"))
    sys.modules["skills.sensory_bridges.scripts.bridge_utils"] = bridge_utils
    video_bridge_module = _load_bridge_module(
        "skills.sensory_bridges.scripts.video_to_agent",
        "video_to_agent.py",
    )
    _extract_keyframes = video_bridge_module._extract_keyframes


SLIDE_CONTACT_SHEET = "winner-slides-contact-sheet.png"
INSPECTION_RECEIPT = "pass2-inspection-pack.json"


def _load_json_object(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError(f"{path.name} must contain a JSON object at the top level")
    return data


def _load_yaml_object(path: Path) -> dict[str, Any]:
    if yaml is None:
        raise RuntimeError("PyYAML is required for motion_plan.yaml")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path.name} must contain a YAML mapping at the top level")
    return data


def _load_authorized_slides(bundle_dir: Path) -> list[dict[str, Any]]:
    authorized_path = bundle_dir / "authorized-storyboard.json"
    authorized = _load_json_object(authorized_path)
    slides = authorized.get("authorized_slides", [])
    if not isinstance(slides, list) or not slides:
        raise ValueError("authorized-storyboard.json must contain a non-empty authorized_slides array")
    ordered = [row for row in slides if isinstance(row, dict)]
    ordered.sort(key=lambda row: int(row.get("card_number", 0)))
    return ordered


def _load_motion_rows(bundle_dir: Path) -> list[dict[str, Any]]:
    motion_plan_path = bundle_dir / "motion_plan.yaml"
    if not motion_plan_path.is_file():
        return []
    motion_plan = _load_yaml_object(motion_plan_path)
    rows = motion_plan.get("slides", [])
    if not isinstance(rows, list):
        return []
    return [row for row in rows if isinstance(row, dict)]


def _fit_cover(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    target_w, target_h = size
    src_w, src_h = image.size
    scale = max(target_w / src_w, target_h / src_h)
    resized = image.resize((max(1, int(src_w * scale)), max(1, int(src_h * scale))), Image.Resampling.LANCZOS)
    left = max(0, (resized.width - target_w) // 2)
    top = max(0, (resized.height - target_h) // 2)
    return resized.crop((left, top, left + target_w, top + target_h))


def _build_contact_sheet(
    image_paths: list[Path],
    *,
    labels: list[str],
    output_path: Path,
    thumb_size: tuple[int, int] = (320, 180),
    columns: int = 3,
    header: str | None = None,
) -> Path:
    if not image_paths:
        raise ValueError("image_paths must not be empty")
    if len(image_paths) != len(labels):
        raise ValueError("labels must align with image_paths")

    padding = 20
    label_height = 34
    header_height = 48 if header else 0
    rows = math.ceil(len(image_paths) / columns)
    canvas_w = padding + columns * (thumb_size[0] + padding)
    canvas_h = header_height + padding + rows * (thumb_size[1] + label_height + padding)
    canvas = Image.new("RGB", (canvas_w, canvas_h), color=(248, 248, 248))
    draw = ImageDraw.Draw(canvas)

    if header:
        draw.text((padding, 14), header, fill=(20, 20, 20))

    for index, (image_path, label) in enumerate(zip(image_paths, labels, strict=False)):
        row = index // columns
        col = index % columns
        x = padding + col * (thumb_size[0] + padding)
        y = header_height + padding + row * (thumb_size[1] + label_height + padding)
        with Image.open(image_path) as image:
            thumb = _fit_cover(image.convert("RGB"), thumb_size)
        canvas.paste(thumb, (x, y))
        draw.rectangle((x, y, x + thumb_size[0], y + thumb_size[1]), outline=(180, 180, 180), width=1)
        draw.text((x, y + thumb_size[1] + 8), label, fill=(30, 30, 30))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output_path)
    return output_path


def build_pass2_inspection_pack(
    bundle_dir: str | Path,
    *,
    max_motion_frames: int = 6,
) -> dict[str, Any]:
    bundle = Path(bundle_dir).resolve()
    if not bundle.is_dir():
        raise FileNotFoundError(f"Bundle directory not found: {bundle}")

    inspection_dir = bundle / "recovery" / "inspection"
    inspection_dir.mkdir(parents=True, exist_ok=True)

    authorized_slides = _load_authorized_slides(bundle)
    slide_paths = [Path(str(row["file_path"])).resolve() for row in authorized_slides]
    slide_labels = [f"{int(row['card_number']):02d} {row['slide_id']}" for row in authorized_slides]
    slide_sheet_path = _build_contact_sheet(
        slide_paths,
        labels=slide_labels,
        output_path=inspection_dir / SLIDE_CONTACT_SHEET,
        columns=3,
        header="Winner Slides",
    )

    motion_rows = [
        row for row in _load_motion_rows(bundle)
        if str(row.get("motion_type") or "static").strip().lower() != "static"
        and str(row.get("motion_status") or "").strip().lower() == "approved"
        and str(row.get("motion_asset_path") or "").strip()
    ]

    motion_entries: list[dict[str, Any]] = []
    for row in motion_rows:
        slide_id = str(row.get("slide_id") or "").strip()
        motion_asset = Path(str(row["motion_asset_path"])).resolve()
        frame_dir = inspection_dir / slide_id
        frame_dir.mkdir(parents=True, exist_ok=True)
        frame_records = _extract_keyframes(
            motion_asset,
            frame_dir,
            max_frames=max_motion_frames,
        )
        frame_paths = [Path(record["frame_path"]).resolve() for record in frame_records]
        if not frame_paths:
            continue
        sheet_path = _build_contact_sheet(
            frame_paths,
            labels=[f"{idx + 1}" for idx in range(len(frame_paths))],
            output_path=inspection_dir / f"{slide_id}-motion-contact-sheet.png",
            columns=min(3, len(frame_paths)),
            header=f"{slide_id} motion keyframes",
        )
        motion_entries.append(
            {
                "slide_id": slide_id,
                "motion_asset_path": str(motion_asset),
                "frame_paths": [str(path) for path in frame_paths],
                "contact_sheet_path": str(sheet_path),
            }
        )

    receipt = {
        "status": "built",
        "bundle_path": str(bundle),
        "inspection_dir": str(inspection_dir),
        "winner_slide_contact_sheet": str(slide_sheet_path),
        "winner_slide_count": len(authorized_slides),
        "motion_inspection": motion_entries,
    }
    receipt_path = inspection_dir / INSPECTION_RECEIPT
    receipt_path.write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    receipt["receipt_path"] = str(receipt_path)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Prompt 8 inspection artifacts")
    parser.add_argument("--bundle", type=Path, required=True, help="Tracked source bundle directory")
    parser.add_argument(
        "--max-motion-frames",
        type=int,
        default=6,
        help="Maximum keyframes to include for each approved motion asset",
    )
    args = parser.parse_args()

    try:
        result = build_pass2_inspection_pack(
            args.bundle,
            max_motion_frames=args.max_motion_frames,
        )
        print(json.dumps(result, indent=2))
        return 0
    except Exception as exc:
        print(
            json.dumps(
                {
                    "status": "fail",
                    "errors": [f"inspection_pack_exception: {type(exc).__name__}: {exc}"],
                },
                indent=2,
            )
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
