"""Per-slide variant selection — parse the Storyboard-A chooser code, validate coverage.

The chooser page (gh-pages) emits a human-readable code the operator pastes back as the
G2B verdict ``edit_payload``: ``SBA-<run_tag>-1:A 2:B 3:A ...`` (1-based slide index :
variant). This module turns that into a ``{slide_id: variant}`` map and fail-louds on any
gap so a partial/stale pick can never silently default downstream (Winston/Murat invariant:
exactly one chosen variant per slide, total coverage, keyed by slide_id not index).
"""

from __future__ import annotations

import re

_CODE_RE = re.compile(r"^\s*SBA-(?P<tag>[A-Za-z0-9_-]+)-(?P<body>.+?)\s*$")
_PAIR_RE = re.compile(r"(\d+)\s*:\s*([ABab])")


class SlideVariantSelectionError(ValueError):  # noqa: N818
    """Per-slide variant selection is malformed, incomplete, or references unknown slides."""


def parse_selection_code(code: str, slide_ids_in_order: list[str]) -> dict[str, str]:
    """Parse ``SBA-<tag>-1:A 2:B ...`` into ``{slide_id: "A"|"B"}``.

    The 1-based index maps to ``slide_ids_in_order`` (Gary's slide order). Fail-loud on a
    malformed code, out-of-range or repeated index. Coverage vs the real deck is checked
    separately by :func:`validate_selections` (this only parses what was provided).
    """
    raw = (code or "").strip()
    match = _CODE_RE.match(raw)
    if not match:
        raise SlideVariantSelectionError(
            f"selection code must look like 'SBA-<tag>-1:A 2:B ...'; got {code!r}"
        )
    pairs = _PAIR_RE.findall(match.group("body"))
    if not pairs:
        raise SlideVariantSelectionError(
            f"selection code carries no '<index>:<A|B>' pairs: {code!r}"
        )
    n = len(slide_ids_in_order)
    selections: dict[str, str] = {}
    seen: set[int] = set()
    for idx_s, variant in pairs:
        idx = int(idx_s)
        if idx < 1 or idx > n:
            raise SlideVariantSelectionError(
                f"selection index {idx} out of range 1..{n}"
            )
        if idx in seen:
            raise SlideVariantSelectionError(f"selection index {idx} appears more than once")
        seen.add(idx)
        selections[slide_ids_in_order[idx - 1]] = variant.upper()
    return selections


def validate_selections(
    selections: dict[str, str],
    variants_by_slide: dict[str, set[str]],
) -> None:
    """Fail-loud total-coverage + identity + asset check.

    Every real slide must have exactly one chosen variant; no orphan slide ids; the chosen
    variant must actually exist for that slide. Raises naming the offending slide id(s) —
    never silently defaults (a silent default is the deck-wide failure mode in disguise).
    """
    all_ids = set(variants_by_slide)
    chosen_ids = set(selections)
    missing = sorted(all_ids - chosen_ids)
    if missing:
        raise SlideVariantSelectionError(
            f"per-slide selection is missing a choice for slide(s): {missing}"
        )
    extra = sorted(chosen_ids - all_ids)
    if extra:
        raise SlideVariantSelectionError(
            f"per-slide selection references slide(s) not in the deck: {extra}"
        )
    for slide_id, variant in selections.items():
        available = variants_by_slide[slide_id]
        if variant not in available:
            raise SlideVariantSelectionError(
                f"slide {slide_id!r} has no variant {variant!r}; available: {sorted(available)}"
            )


def run_tag_for_trial(trial_id: object) -> str:
    """Short, stable tag (first 8 hex of the trial id) used as the chooser code's SBA prefix
    so a stale paste from a different run is detectable."""
    return str(trial_id).replace("-", "")[:8]


__all__ = [
    "SlideVariantSelectionError",
    "parse_selection_code",
    "run_tag_for_trial",
    "validate_selections",
]
