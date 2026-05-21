# /// script
# requires-python = ">=3.10"
# ///
"""Validate Gary dispatch payload readiness for HIL Gate 2.

This gate is run after Gary dispatch/export and before Irene Pass 2 handoff.
It enforces strict dispatch contract requirements by calling
`gamma_operations.validate_dispatch_ready()` and adds sequencing checks.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover - optional for yaml input
    yaml = None  # type: ignore[assignment]

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

GAMMA_SCRIPTS_DIR = PROJECT_ROOT / "skills" / "gamma-api-mastery" / "scripts"
if str(GAMMA_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(GAMMA_SCRIPTS_DIR))

from gamma_operations import validate_dispatch_ready  # type: ignore[import-not-found]  # noqa: E402


def _load_payload(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    suffix = path.suffix.lower()

    if suffix in {".yml", ".yaml"}:
        if yaml is None:
            raise RuntimeError("PyYAML is required for YAML input payloads")
        data = yaml.safe_load(text)
    else:
        data = json.loads(text)

    if not isinstance(data, dict):
        raise ValueError("Gary dispatch payload must be an object at the top level")
    return data


def _parse_literal_visual_specs(irene_pass1_path: Path) -> dict[int, dict[str, str]]:
    text = irene_pass1_path.read_text(encoding="utf-8")
    if "## literal-visual spec cards" not in text:
        return {}

    section = text.split("## literal-visual spec cards", 1)[1]
    next_heading = section.find("\n## ")
    if next_heading != -1:
        section = section[:next_heading]

    specs: dict[int, dict[str, str]] = {}
    blocks = re.split(r"\n###\s+", section)
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        lines = block.splitlines()
        fields: dict[str, str] = {}
        for line in lines[1:]:
            stripped = line.strip()
            if not stripped.startswith("- ") or ":" not in stripped:
                continue
            key, value = stripped[2:].split(":", 1)
            fields[key.strip()] = value.strip()
        slide_number = fields.get("slide_number")
        if slide_number and slide_number.isdigit():
            specs[int(slide_number)] = fields
    return specs


def _load_diagram_cards(bundle_dir: Path) -> list[dict[str, Any]]:
    path = bundle_dir / "gary-diagram-cards.json"
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        cards = data.get("cards", [])
        return cards if isinstance(cards, list) else []
    return []


_PLANNING_DIRECTIVE_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"instructional content aligned to", re.IGNORECASE),
]

_HTTP_URL_PATTERN = re.compile(r"https?://\S+", re.IGNORECASE)


def _validate_literal_text_content_bearing(
    bundle_dir: Path,
    dispatch_metadata: dict[str, Any],
) -> list[str]:
    """Check that literal-text slides in gary-slide-content.json contain real
    source text, not Irene planning directives.

    Requires both gary-slide-content.json (via dispatch_metadata) and
    gary-fidelity-slides.json to be present. If either is absent the check
    is skipped gracefully so older run artifacts are not broken.

    Returns a list of error strings (empty = pass).
    """
    errors: list[str] = []

    fidelity_path = bundle_dir / "gary-fidelity-slides.json"
    if not fidelity_path.exists():
        return errors  # graceful skip -- older run without fidelity file

    slides_content_json_path = str(
        dispatch_metadata.get("slides_content_json_path") or ""
    ).strip()
    if not slides_content_json_path:
        return errors  # already caught by dispatch_metadata check

    content_path = (bundle_dir / slides_content_json_path).resolve()
    if not content_path.is_file():
        # Try relative to project root
        content_path = (PROJECT_ROOT / slides_content_json_path).resolve()
    if not content_path.is_file():
        return errors  # file missing -- structural check already handles absence

    try:
        fidelity_data = json.loads(fidelity_path.read_text(encoding='utf-8'))
        content_data = json.loads(content_path.read_text(encoding='utf-8'))
    except (json.JSONDecodeError, OSError):
        return errors  # parse failures are separate concerns

    fidelity_slides: list[dict[str, Any]] = fidelity_data.get('slides', [])
    literal_text_numbers: set[int] = {
        int(s["slide_number"])
        for s in fidelity_slides
        if isinstance(s, dict)
        and str(s.get('fidelity', '')).strip().lower() == 'literal-text'
        and isinstance(s.get('slide_number'), int)
    }

    if not literal_text_numbers:
        return errors

    content_slides: list[dict[str, Any]] = content_data.get('slides', [])
    for slide in content_slides:
        if not isinstance(slide, dict):
            continue
        slide_number = slide.get('slide_number')
        if not isinstance(slide_number, int) or slide_number not in literal_text_numbers:
            continue
        content_field = str(slide.get('content') or '').strip()
        for pattern in _PLANNING_DIRECTIVE_PATTERNS:
            if pattern.search(content_field):
                errors.append(
                    f"gary-slide-content.json slide {slide_number} (literal-text) "
                    f"content field contains a planning directive rather than actual "
                    f"source text (matched pattern: {pattern.pattern!r}). "
                    f"For textMode=preserve, Gamma renders this text verbatim on screen. "
                    f"Replace with the extracted source text from extracted.md anchor."
                )
                break  # one error per slide is sufficient

    return errors


def _validate_literal_visual_image_only_content(
    bundle_dir: Path,
    dispatch_metadata: dict[str, Any],
) -> list[str]:
    """Check literal-visual slides are image-only at dispatch payload level.

    Policy: literal-visual on-slide payload must not include substantive text.
    Any explanatory text belongs in Irene Pass 2 narration/script.
    """
    errors: list[str] = []

    fidelity_path = bundle_dir / "gary-fidelity-slides.json"
    if not fidelity_path.exists():
        return errors

    slides_content_json_path = str(
        dispatch_metadata.get("slides_content_json_path") or ""
    ).strip()
    if not slides_content_json_path:
        return errors

    content_path = (bundle_dir / slides_content_json_path).resolve()
    if not content_path.is_file():
        content_path = (PROJECT_ROOT / slides_content_json_path).resolve()
    if not content_path.is_file():
        return errors

    try:
        fidelity_data = json.loads(fidelity_path.read_text(encoding="utf-8"))
        content_data = json.loads(content_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return errors

    fidelity_slides: list[dict[str, Any]] = fidelity_data.get("slides", [])
    literal_visual_numbers: set[int] = {
        int(s["slide_number"])
        for s in fidelity_slides
        if isinstance(s, dict)
        and str(s.get("fidelity", "")).strip().lower() == "literal-visual"
        and isinstance(s.get("slide_number"), int)
    }

    if not literal_visual_numbers:
        return errors

    content_slides: list[dict[str, Any]] = content_data.get("slides", [])
    for slide in content_slides:
        if not isinstance(slide, dict):
            continue
        slide_number = slide.get("slide_number")
        if not isinstance(slide_number, int) or slide_number not in literal_visual_numbers:
            continue

        content_field = str(slide.get("content") or "").strip()
        if not content_field:
            continue

        residue = _HTTP_URL_PATTERN.sub("", content_field).strip()
        if residue:
            errors.append(
                f"gary-slide-content.json slide {slide_number} (literal-visual) "
                "contains on-slide text payload. Policy requires literal-visual slides "
                "to be image-only; move explanatory text to Irene Pass 2 narration/script."
            )

    return errors


def _infer_gamma_asset_family(url: str) -> str:
    normalized = url.lower()
    if "/generated-images/" in normalized:
        return "generated-images"
    if "/design-anything/" in normalized:
        return "design-anything"
    return "other"


def _is_remote_http_ref(value: str) -> bool:
    parsed = urlparse(str(value).strip())
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _resolve_existing_local_path(path_value: str, *, bundle_dir: Path) -> Path | None:
    candidate = Path(path_value)
    if candidate.is_absolute():
        return candidate if candidate.is_file() else None

    bundle_candidate = (bundle_dir / candidate).resolve()
    if bundle_candidate.is_file():
        return bundle_candidate

    project_candidate = (PROJECT_ROOT / candidate).resolve()
    if project_candidate.is_file():
        return project_candidate

    return None


def _validate_literal_visual_authority(bundle_dir: Path) -> list[str]:
    errors: list[str] = []
    irene_pass1_path = bundle_dir / "irene-pass1.md"
    if not irene_pass1_path.exists():
        return errors

    specs = _parse_literal_visual_specs(irene_pass1_path)
    if not specs:
        return errors

    diagram_cards = _load_diagram_cards(bundle_dir)
    card_map = {
        card.get("card_number"): card
        for card in diagram_cards
        if isinstance(card, dict) and isinstance(card.get("card_number"), int)
    }

    spec_card_numbers = sorted(specs)
    diagram_card_numbers = sorted(card_map)
    if diagram_card_numbers != spec_card_numbers:
        errors.append(
            "gary-diagram-cards.json card_number set must exactly match Irene Pass 1 "
            f"literal-visual cards. expected={spec_card_numbers} actual={diagram_card_numbers}"
        )

    for card_number, spec in specs.items():
        card = card_map.get(card_number)
        if card is None:
            continue

        expected_source_asset = spec.get("source_asset", "")
        expected_treatment = spec.get("image_treatment", "")
        layout_constraint = spec.get("layout_constraint", "")

        actual_source_asset = str(card.get("source_asset", "")).strip()
        derivation_type = str(card.get("derivation_type", "")).strip()
        image_url = str(card.get("image_url", "")).strip()
        asset_family = _infer_gamma_asset_family(image_url)

        if expected_source_asset and actual_source_asset != expected_source_asset:
            errors.append(
                f"literal-visual card {card_number} source_asset mismatch: "
                f"expected {expected_source_asset!r} but found {actual_source_asset!r}"
            )

        requires_source_derived = expected_treatment == "source-crop" or any(
            phrase in layout_constraint.lower()
            for phrase in ("no redrawn substitute", "do not fabricate")
        )
        if not requires_source_derived:
            continue

        if derivation_type not in {"source-crop", "rebranded-source", "user-provided-exact"}:
            errors.append(
                f"literal-visual card {card_number} must declare a source-derived derivation_type "
                f"for Irene image_treatment=source-crop; found {derivation_type!r}"
            )

        if asset_family == "generated-images":
            errors.append(
                f"literal-visual card {card_number} uses a Gamma generated-images asset for a "
                "source-crop slide; dispatch must fail closed until a source-derived image is staged"
            )

    return errors


def _validate_preintegration_publish_receipt(
    payload: dict[str, Any],
    *,
    bundle_dir: Path,
) -> list[str]:
    errors: list[str] = []
    diagram_cards = _load_diagram_cards(bundle_dir)
    expected_preintegration_cards: list[int] = []

    for card in diagram_cards:
        if not isinstance(card, dict):
            continue
        card_number = card.get("card_number")
        if not isinstance(card_number, int):
            continue
        preintegration_png_path = str(card.get("preintegration_png_path", "")).strip()
        image_url = str(card.get("image_url", "")).strip()
        if preintegration_png_path or (image_url and not _is_remote_http_ref(image_url)):
            expected_preintegration_cards.append(card_number)

    if not expected_preintegration_cards:
        return errors

    dispatch_metadata = payload.get("dispatch_metadata")
    if not isinstance(dispatch_metadata, dict):
        dispatch_metadata = {}

    site_repo_url = str(
        dispatch_metadata.get("site_repo_url")
        or payload.get("site_repo_url")
        or ""
    ).strip()
    if not site_repo_url:
        errors.append(
            "site_repo_url must be present when diagram cards use local preintegration paths"
        )

    invocation_mode = str(
        dispatch_metadata.get("invocation_mode")
        or payload.get("invocation_mode")
        or payload.get("mode")
        or payload.get("execution_mode")
        or ""
    ).strip().lower()
    if invocation_mode in {"ad-hoc", "adhoc"}:
        errors.append(
            "Local preintegration paths are not allowed in ad-hoc mode; "
            "use tracked/default mode or provide hosted HTTPS image_url values"
        )
    elif invocation_mode not in {"", "tracked", "default"}:
        errors.append(
            "invocation_mode must be tracked/default when local preintegration "
            f"paths are used; found {invocation_mode!r}"
        )

    receipt = payload.get("literal_visual_publish")
    if not isinstance(receipt, dict):
        errors.append(
            "literal_visual_publish must be present when diagram cards use local "
            "preintegration paths"
        )
        return errors

    if not bool(receipt.get("preintegration_ready")):
        errors.append(
            "literal_visual_publish.preintegration_ready must be true when local "
            "preintegration paths were supplied"
        )

    substituted_cards = receipt.get("substituted_cards")
    if not isinstance(substituted_cards, list):
        errors.append(
            "literal_visual_publish.substituted_cards must be an array when local "
            "preintegration paths are supplied"
        )
        return errors

    substituted_set = {
        int(card) for card in substituted_cards if isinstance(card, int)
    }
    expected_set = set(expected_preintegration_cards)
    if expected_set - substituted_set:
        missing = sorted(expected_set - substituted_set)
        errors.append(
            "literal_visual_publish.substituted_cards missing card_number(s): "
            + ", ".join(str(v) for v in missing)
        )

    return errors


def _card_sequence(slides: list[dict[str, Any]]) -> list[int]:
    return [item.get("card_number") for item in slides if isinstance(item, dict)]


def validate_gary_dispatch_ready(
    payload: dict[str, Any],
    *,
    payload_path: Path | None = None,
) -> dict[str, Any]:
    """Validate dispatch payload for Gate 2 readiness."""
    errors: list[str] = []

    slides = payload.get("gary_slide_output")
    if not isinstance(slides, list):
        errors.append("gary_slide_output must be an array")
        slides = []

    if isinstance(slides, list) and len(slides) == 0:
        errors.append("gary_slide_output must contain at least one slide for Gate 2 review")

    try:
        validate_dispatch_ready(payload)
    except ValueError as exc:
        errors.append(str(exc))

    missing_local_png_for: list[str] = []
    invalid_non_png_for: list[str] = []
    remote_file_path_for: list[str] = []
    bundle_dir = payload_path.parent if payload_path is not None else None

    if isinstance(slides, list):
        for item in slides:
            if not isinstance(item, dict):
                continue
            slide_label = str(item.get("slide_id") or item.get("card_number") or "unknown")
            file_path = str(item.get("file_path") or "").strip()
            if not file_path:
                continue
            if _is_remote_http_ref(file_path):
                remote_file_path_for.append(slide_label)
                continue
            if Path(file_path).suffix.lower() != ".png":
                invalid_non_png_for.append(slide_label)
            if bundle_dir is not None and _resolve_existing_local_path(file_path, bundle_dir=bundle_dir) is None:
                missing_local_png_for.append(slide_label)

    if remote_file_path_for:
        errors.append(
            "gary_slide_output file_path must reference local downloaded PNGs; remote path found for: "
            + ", ".join(remote_file_path_for)
        )
    if invalid_non_png_for:
        errors.append(
            "gary_slide_output file_path must end with .png for: "
            + ", ".join(invalid_non_png_for)
        )
    if missing_local_png_for:
        errors.append(
            "gary_slide_output file_path does not exist on disk for: "
            + ", ".join(missing_local_png_for)
        )

    card_sequence = _card_sequence(slides)
    is_double_dispatch = bool(
        payload.get("generation_mode") == "double-dispatch"
        or payload.get("double_dispatch", {}).get("enabled")
    )
    if is_double_dispatch:
        # In double-dispatch, each card_number appears exactly twice (A+B)
        # EXCEPT interstitials with double_dispatch_eligible == false (appear once).
        unique_cards = sorted(set(card_sequence))
        contiguous_from_one = (
            bool(unique_cards)
            and all(isinstance(n, int) for n in unique_cards)
            and unique_cards == list(range(1, len(unique_cards) + 1))
        )
        # Build expected count per card: interstitials with dd_eligible=false → 1, else → 2
        expected_count_by_card: dict[int, int] = {}
        for item in slides:
            if not isinstance(item, dict):
                continue
            cn = item.get("card_number")
            if isinstance(cn, int):
                if item.get("double_dispatch_eligible") is False:
                    expected_count_by_card[cn] = 1
                else:
                    expected_count_by_card.setdefault(cn, 2)
        from collections import Counter
        counts = Counter(card_sequence)
        bad_counts = {
            k: v for k, v in counts.items()
            if v != expected_count_by_card.get(k, 2)
        }
        if bad_counts:
            errors.append(
                f"double-dispatch: card_number count mismatch; "
                f"mismatched: {bad_counts}"
            )
    else:
        contiguous_from_one = (
            bool(card_sequence)
            and all(isinstance(n, int) for n in card_sequence)
            and card_sequence == list(range(1, len(card_sequence) + 1))
        )
    if card_sequence and not contiguous_from_one:
        errors.append(
            "gary_slide_output card_number sequence must be contiguous and start at 1 (1..N)"
        )

    dispatch_metadata = payload.get("dispatch_metadata")
    if not isinstance(dispatch_metadata, dict):
        errors.append(
            "dispatch_metadata must be present - re-run dispatch with the current "
            "gamma_operations.py to embed content source provenance"
        )
    elif not str(dispatch_metadata.get("slides_content_json_path") or "").strip():
        errors.append(
            "dispatch_metadata.slides_content_json_path must be non-empty - "
            "dispatch must use --slides-content-json to prevent placeholder content"
        )

    if payload_path is not None:
        errors.extend(_validate_literal_visual_authority(payload_path.parent))
        errors.extend(
            _validate_preintegration_publish_receipt(payload, bundle_dir=payload_path.parent)
        )
        if isinstance(dispatch_metadata, dict):
            errors.extend(
                _validate_literal_text_content_bearing(
                    payload_path.parent, dispatch_metadata
                )
            )
            errors.extend(
                _validate_literal_visual_image_only_content(
                    payload_path.parent, dispatch_metadata
                )
            )

    return {
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "checks": {
            "slide_count": len(slides),
            "card_sequence": card_sequence,
            "contiguous_from_one": contiguous_from_one,
            "missing_local_png_for": missing_local_png_for,
            "invalid_non_png_for": invalid_non_png_for,
            "remote_file_path_for": remote_file_path_for,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Gary dispatch payload readiness")
    parser.add_argument(
        "--payload",
        type=Path,
        required=True,
        help="Path to Gary dispatch payload JSON/YAML",
    )
    args = parser.parse_args()

    try:
        payload = _load_payload(args.payload)
        result = validate_gary_dispatch_ready(payload, payload_path=args.payload)
        print(json.dumps(result, indent=2))
        return 0 if result["status"] == "pass" else 1
    except Exception as exc:
        print(
            json.dumps(
                {
                    "status": "fail",
                    "errors": [f"validator_exception: {type(exc).__name__}: {exc}"],
                },
                indent=2,
            )
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
