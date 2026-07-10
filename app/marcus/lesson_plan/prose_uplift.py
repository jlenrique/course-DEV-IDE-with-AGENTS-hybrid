"""Learner-ready workbook prose uplift (Mine 6).

SME-aware ``prose_revoicer`` that removes REVOICE markers, reduces deixis,
and stamps attribution from Mine 3 ``resolve_sme_profile``. Idempotent on
second pass (Murat negative #6).
"""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass

from app.marcus.course_source.sme_registry import SmeProfile, resolve_sme_profile
from app.marcus.lesson_plan.workbook_producer import (
    REVOICE_REQUIRED_MARKER,
    default_prose_revoicer,
)

ProseRevoicer = Callable[[str, str], str]

# Deixis / slide-bound phrases that learner-ready prose should not lean on.
_DEIXIS_PATTERNS: tuple[re.Pattern[str], ...] = tuple(
    re.compile(p, re.IGNORECASE)
    for p in (
        r"\bhere you see\b",
        r"\bthis chart\b",
        r"\bon the slide\b",
        r"\bas shown (here|above|below)\b",
        r"\blook at (this|the)\b",
        r"\bthis figure\b",
        r"\bin this slide\b",
        r"\bas you can see\b",
        r"\bclick (here|next)\b",
    )
)

_BLOCKQUOTE_LINE = re.compile(r"^>\s?", re.MULTILINE)


@dataclass(frozen=True)
class ProseUpliftDelta:
    """Measurable before/after metrics for a revoiced segment or document."""

    revoice_marker_before: int
    revoice_marker_after: int
    deixis_hits_before: int
    deixis_hits_after: int
    chars_before: int
    chars_after: int

    @property
    def deixis_reduced(self) -> bool:
        return self.deixis_hits_after <= self.deixis_hits_before

    @property
    def markers_cleared(self) -> bool:
        return self.revoice_marker_before > 0 and self.revoice_marker_after == 0

    def to_dict(self) -> dict[str, int | bool]:
        return {
            "revoice_marker_before": self.revoice_marker_before,
            "revoice_marker_after": self.revoice_marker_after,
            "deixis_hits_before": self.deixis_hits_before,
            "deixis_hits_after": self.deixis_hits_after,
            "chars_before": self.chars_before,
            "chars_after": self.chars_after,
            "deixis_reduced": self.deixis_reduced,
            "markers_cleared": self.markers_cleared,
        }


def count_revoice_markers(text: str) -> int:
    """Count REVOICE-REQUIRED honesty markers in text."""
    return text.count(REVOICE_REQUIRED_MARKER)


def count_deixis_hits(text: str) -> int:
    """Count deixis / slide-bound phrase hits."""
    return sum(len(p.findall(text)) for p in _DEIXIS_PATTERNS)


def measure_prose_delta(before: str, after: str) -> ProseUpliftDelta:
    """Compute measurable before/after prose uplift delta."""
    return ProseUpliftDelta(
        revoice_marker_before=count_revoice_markers(before),
        revoice_marker_after=count_revoice_markers(after),
        deixis_hits_before=count_deixis_hits(before),
        deixis_hits_after=count_deixis_hits(after),
        chars_before=len(before),
        chars_after=len(after),
    )


def _strip_scaffold(text: str) -> str:
    """Remove REVOICE markers and leading blockquote scaffolding."""
    cleaned = text.replace(REVOICE_REQUIRED_MARKER, "")
    cleaned = _BLOCKQUOTE_LINE.sub("", cleaned)
    return cleaned.strip()


def _rewrite_deixis(text: str) -> str:
    """Replace common deixis with self-contained learner-ready phrasing."""
    replacements = (
        (r"\bhere you see\b", "the material shows"),
        (r"\bthis chart\b", "the chart"),
        (r"\bon the slide\b", "in the lesson"),
        (r"\bas shown (here|above|below)\b", "as described"),
        (r"\blook at (this|the)\b", r"consider \1"),
        (r"\bthis figure\b", "the figure"),
        (r"\bin this slide\b", "in this section"),
        (r"\bas you can see\b", "notably"),
        (r"\bclick (here|next)\b", "continue"),
    )
    out = text
    for pattern, repl in replacements:
        out = re.sub(pattern, repl, out, flags=re.IGNORECASE)
    return out


def uplift_narration_text(narration_text: str, *, profile: SmeProfile) -> str:
    """Transform scaffold narration into learner-ready prose for one SME."""
    body = _strip_scaffold(narration_text)
    # If input was already uplifted (idempotent), strip prior attribution footer
    body = re.sub(
        r"\n*---\n\*Voice profile:.*\*\s*$",
        "",
        body,
        flags=re.DOTALL,
    ).strip()
    body = _rewrite_deixis(body)
    if not body:
        body = "(No narration text available for this segment.)"
    # Ensure we do not re-introduce the REVOICE marker
    body = body.replace(REVOICE_REQUIRED_MARKER, "").strip()
    attribution = profile.attribution.strip()
    voice_ref = profile.voice_profile_ref.strip()
    footer = (
        f"\n\n---\n*Voice profile: {voice_ref} — {attribution}*"
        if attribution
        else f"\n\n---\n*Voice profile: {voice_ref}*"
    )
    return f"{body}{footer}\n"


def sme_aware_prose_revoicer(sme_key_or_name: str) -> ProseRevoicer:
    """Return a ``prose_revoicer`` bound to a Mine 3 SME profile."""
    profile = resolve_sme_profile(sme_key_or_name)

    def _revoice(segment_id: str, narration_text: str) -> str:
        _ = segment_id  # available for future segment-scoped voice rules
        return uplift_narration_text(narration_text, profile=profile)

    return _revoice


def prose_revoicer_for_sme(sme_key_or_name: str | None) -> ProseRevoicer:
    """Factory: SME-aware uplift when key present; else default scaffold revoicer."""
    if sme_key_or_name is None or not str(sme_key_or_name).strip():
        return default_prose_revoicer
    return sme_aware_prose_revoicer(str(sme_key_or_name).strip())


__all__ = [
    "ProseUpliftDelta",
    "count_deixis_hits",
    "count_revoice_markers",
    "measure_prose_delta",
    "prose_revoicer_for_sme",
    "sme_aware_prose_revoicer",
    "uplift_narration_text",
]
