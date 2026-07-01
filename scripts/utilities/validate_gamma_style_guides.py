"""Hermetic offline write-gate for the CD-owned Gamma styleguide library.

The operator-required "copacetic-quality audit" of
``state/config/gamma-style-guides.yaml``. Runs OFFLINE / in CI with NO network.
The only network-touching path is the ``--check-existence`` flag (OFF by default),
which live-verifies theme/template ids against the Gamma API.

Enforces (spec §2):
- completeness with INVERTED polarity: a null/"default"/empty REQUIRED surface field
  FAILS (a present value is the passing state, absence is the failure);
- FROZEN enums reused from ``app/specialists/gary/_act.py`` (never re-derived);
- discriminated-union: ``production_mode: studio`` FORBIDS the Classic-only surface
  (``gamma.styleguide.surface-violation``); ``api`` requires a theme + full surface;
- coherence-triad: theme + art-style/keywords + dimensions agree and a
  ``presentation.narrative.triad_rationale`` prose is present;
- roster floor: >= 1 Classic (api) and >= 1 Studio guide present.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

# Allow direct CLI invocation (``python scripts/utilities/validate_gamma_style_guides.py``)
# by ensuring the repo root is importable before the ``app`` imports below.
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from app.specialists.gary._act import (  # noqa: E402
    CARD_DIMENSION_VALUES,
    IMAGE_MODEL_VALUES,
    IMAGE_SOURCE_VALUES,
    IMAGE_STYLE_PRESET_VALUES,
    PRODUCTION_MODE_VALUES,
    TEXT_AMOUNT_VALUES,
    TEXT_LANGUAGE_VALUES,
    TEXT_MODE_VALUES,
)
from app.specialists.gary.styleguide_library import (  # noqa: E402
    GAMMA_STYLE_GUIDES_PATH,
    StyleguideError,
    expand_record,
    load_style_guides,
)

# Frozen-enum reuse: {resolved base key -> allowed value set}. Sourced from _act.py.
_ENUM_CHECKS: dict[str, frozenset[str]] = {
    "text_mode": TEXT_MODE_VALUES,
    "amount": TEXT_AMOUNT_VALUES,
    "language": TEXT_LANGUAGE_VALUES,
    "image_style_preset": IMAGE_STYLE_PRESET_VALUES,
    "image_model": IMAGE_MODEL_VALUES,
    "image_source": IMAGE_SOURCE_VALUES,
    "dimensions": CARD_DIMENSION_VALUES,
}


def _is_present(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return value.strip() not in {"", "default"}
    if isinstance(value, (list, tuple, set, dict)):
        return bool(value)
    return True


def _triad_rationale(record: dict[str, Any]) -> Any:
    return ((record.get("presentation") or {}).get("narrative") or {}).get("triad_rationale")


def _validate_one(name: str, record: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not isinstance(record, dict):
        return [f"{name}: styleguide record must be a mapping"]

    production_mode = str(record.get("production_mode") or "").strip().lower()
    if production_mode not in PRODUCTION_MODE_VALUES:
        errors.append(
            f"{name}: production_mode must be one of {sorted(PRODUCTION_MODE_VALUES)}; "
            f"got {record.get('production_mode')!r}"
        )
        # Without a valid discriminant the rest of the checks are undefined.
        return errors

    # --- Discriminated-union surface + expansion (shares Gary's resolver) ---------
    try:
        resolved = expand_record(record, name=name)
    except StyleguideError as exc:
        errors.append(f"{name}: {exc} [{exc.tag}]")
        resolved = {}

    # --- Completeness, INVERTED polarity (null/default/empty on required FAILS) ----
    if production_mode == "api":
        required = {
            "theme.id": (record.get("theme") or {}).get("id"),
            "prompt_configuration.text_content.mode": (
                (record.get("prompt_configuration") or {}).get("text_content") or {}
            ).get("mode"),
            "prompt_configuration.visuals.image_source": (
                (record.get("prompt_configuration") or {}).get("visuals") or {}
            ).get("image_source"),
            "page_settings.card_options.dimensions": (
                (record.get("page_settings") or {}).get("card_options") or {}
            ).get("dimensions"),
        }
    else:  # studio
        required = {
            "studio_template.gamma_id": (record.get("studio_template") or {}).get("gamma_id"),
        }
    for field, value in required.items():
        if not _is_present(value):
            errors.append(
                f"{name}: required field {field} is null/default/empty "
                f"(inverted-polarity completeness failure)"
            )

    # --- Frozen-enum validation on the RESOLVED surface ---------------------------
    for key, allowed in _ENUM_CHECKS.items():
        if key in resolved and str(resolved[key]).strip() not in allowed:
            errors.append(
                f"{name}: {key}={resolved[key]!r} is not one of {sorted(allowed)} "
                f"(frozen enum from _act.py)"
            )

    # --- Cross-field: image_style_preset='custom' REQUIRES a custom_style ----------
    # Gary raises `image_style is required when image_style_preset='custom'` at
    # dispatch; the offline write-gate must reject the same config at write time so a
    # would-crash-at-render style never ships (code-review item #6).
    if str(resolved.get("image_style_preset") or "").strip() == "custom" and not _is_present(
        resolved.get("image_style")
    ):
        errors.append(
            f"{name}: image_style_preset='custom' requires a custom_style "
            f"(visuals.custom_style) or Gary crashes at dispatch"
        )

    # --- Coherence-triad: theme + art-style/keywords + dimensions + prose ----------
    if not _is_present(_triad_rationale(record)):
        errors.append(
            f"{name}: coherence-triad requires a non-empty "
            f"presentation.narrative.triad_rationale prose"
        )
    if production_mode == "api":
        visuals = (record.get("prompt_configuration") or {}).get("visuals") or {}
        art_axis = _is_present(visuals.get("keywords")) or _is_present(
            visuals.get("style_preset")
        ) or _is_present(visuals.get("custom_style"))
        if not art_axis:
            errors.append(
                f"{name}: coherence-triad art axis empty (needs keywords or a "
                f"style_preset/custom_style to agree with theme + dimensions)"
            )
    return errors


def validate_style_guides(
    data: dict[str, Any],
    *,
    check_existence: bool = False,
) -> list[str]:
    """Return a list of validation errors for the styleguide library payload.

    ``check_existence`` is the ONLY network path (theme/template live existence). It
    is OFF by default so the CI/hermetic run never touches the network.
    """
    errors: list[str] = []
    guides = data.get("style_guides")
    if not isinstance(guides, dict) or not guides:
        return ["style_guides mapping is missing or empty"]

    classic_count = 0
    studio_count = 0
    for name in sorted(guides):
        record = guides[name]
        errors.extend(_validate_one(name, record))
        if isinstance(record, dict):
            mode = str(record.get("production_mode") or "").strip().lower()
            if mode == "api":
                classic_count += 1
            elif mode == "studio":
                studio_count += 1

    # --- Roster floor -------------------------------------------------------------
    if classic_count < 1:
        errors.append("roster floor: at least 1 Classic (api) styleguide is required")
    if studio_count < 1:
        errors.append("roster floor: at least 1 Studio styleguide is required")

    if check_existence:
        errors.extend(_check_existence(guides))
    return errors


def _check_existence(guides: dict[str, Any]) -> list[str]:  # pragma: no cover - network
    """Live theme/template existence check (the ONLY network-touching path)."""
    from scripts.api_clients.gamma_client import GammaClient

    errors: list[str] = []
    client = GammaClient()
    # Real Gamma API caps `limit` at 50 (HTTP 400 above it). Pagination beyond
    # the first 50 themes is a filed follow-on (styleguide-validator-live-existence-hardening).
    theme_ids = {t.get("id") for t in client.list_themes(limit=50)}
    for name, record in guides.items():
        if not isinstance(record, dict):
            continue
        if str(record.get("production_mode") or "").strip().lower() == "api":
            theme_id = (record.get("theme") or {}).get("id")
            if theme_id and theme_id not in theme_ids:
                errors.append(f"{name}: theme id {theme_id!r} not found in live Gamma themes")
        # Studio template existence has no cheap list endpoint; a real render is the
        # authoritative check (Leg-A AC#5), so we only note the id here.
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--path",
        type=Path,
        default=GAMMA_STYLE_GUIDES_PATH,
        help="path to gamma-style-guides.yaml",
    )
    parser.add_argument(
        "--check-existence",
        action="store_true",
        help="ALSO live-verify theme/template ids against the Gamma API (network).",
    )
    args = parser.parse_args(argv)

    data = load_style_guides(args.path)
    errors = validate_style_guides(data, check_existence=args.check_existence)
    if errors:
        print(f"FAIL: {len(errors)} styleguide validation error(s):")
        for err in errors:
            print(f"  - {err}")
        return 1
    print(f"OK: {args.path} is copacetic ({len(data.get('style_guides', {}))} styleguide(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
