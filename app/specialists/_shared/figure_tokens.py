"""Shared numeric figure token extraction for narration/perception gates."""

from __future__ import annotations

import re

# Digit groups may include thousands-separators (surface-form precision,
# Mine-next trust T4a / leg4-narration-fidelity-gate-precision-before-flag-on).
# Comma form REQUIRES ≥1 `,xxx` group so `$1200` is not truncated to `$120`.
_NUM = r"\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?"

_FIGURE_RE = re.compile(
    # Vision/OCR can concatenate a decorative currency icon with an adjacent
    # percentage label (for example ``$ 5% GDP``).  The percent suffix is the
    # stronger unit signal, so recognize the complete hybrid span before the
    # ordinary money alternative can consume ``$ 5``.  ``+%`` is the same
    # comparator-bearing percent surface seen in the frozen production slide.
    rf"(?:\$\s*)?\b(?:{_NUM})\s*\+?\s*%"
    rf"|\$\s*(?:{_NUM})(?:\s*(?:trillion|billion)\b|\s*[tb]\b)?"
    rf"|\b(?:{_NUM})x\b",
    re.IGNORECASE,
)

# A money RANGE whose LOW endpoint elides the magnitude unit
# ("$760 to $935 billion") — the unit on the HIGH endpoint governs both.
# The slide / perceived authority typically carries the unit on both
# endpoints ("$760 billion to $935 billion"), so without unit inheritance
# the spoken low endpoint mismatches the perceived one purely on magnitude
# class. Inheritance changes the UNIT only, never the NUMBER, so the
# figure-citation guard remains intact for numbers absent from the slide.
_RANGE_RE = re.compile(
    rf"\$\s*({_NUM})\s*"
    r"(?:to|through|and|[-–—])\s*"
    rf"\$\s*({_NUM})\s*(trillion|billion|[tb])\b",
    re.IGNORECASE,
)

# Percent rounding band: source 18.4% vs deck/narration 18% must not false-halt
# (T4a precision). Absolute percentage-points; digit-form only.
PERCENT_TOLERANCE_PP = 0.6


def _parse_numeric(raw: str) -> float:
    return float(raw.replace(",", ""))


def _figures(text: str) -> set[str]:
    tokens: set[str] = set()
    consumed: list[tuple[int, int]] = []
    for match in _RANGE_RE.finditer(text):
        unit = match.group(3).lower()
        tokens.add(_normalize_money(_parse_numeric(match.group(1)), unit))
        tokens.add(_normalize_money(_parse_numeric(match.group(2)), unit))
        consumed.append((match.start(), match.end()))
    for match in _FIGURE_RE.finditer(text):
        if any(start <= match.start() < end for start, end in consumed):
            continue
        tokens.add(_normalize_figure(match.group(0)))
    return tokens


def _normalize_money(number: float, unit: str | None) -> str:
    if unit in ("trillion", "t"):
        return f"money-trillion:{number:g}"
    if unit in ("billion", "b"):
        return f"money-trillion:{number / 1000.0:g}"
    return f"money-bare:{number:g}"


def _normalize_figure(value: str) -> str:
    token = re.sub(r"\s+", "", value.lower()).replace(",", "")
    # A token merely ending in %/x or starting with $ is NOT necessarily a
    # figure — e.g. a DOI / retrieval reference like
    # ``retrieval:scite:10.1057/s41599-024-03196-x`` ends in "x" but is not a
    # multiple. Guard the numeric parses so a non-numeric token falls through to
    # an opaque token instead of crashing the numeric-provenance audit
    # (surfaced by the 35.7 re-witness run at node 08 / research supplements).
    try:
        if token.endswith("%"):
            percent = token[:-1].removeprefix("$").removesuffix("+")
            return f"percent:{float(percent):g}"
        if token.startswith("$"):
            match = re.search(r"\d+(?:\.\d+)?", token)
            if match is None:
                return token
            number = float(match.group(0))
            if "trillion" in token or token.endswith("t"):
                unit: str | None = "trillion"
            elif "billion" in token or token.endswith("b"):
                unit = "billion"
            else:
                unit = None
            return _normalize_money(number, unit)
        if token.endswith("x"):
            return f"multiple:{float(token[:-1]):g}"
    except ValueError:
        return token
    return token


def _figure_near_match(figure: str, source_figures: set[str]) -> bool:
    """True when ``figure`` is an exact or precision-tolerant match to source.

    T4a: percent tokens within ``PERCENT_TOLERANCE_PP`` of a same-kind source
    token count as sourced (18.4% → 18%). Exact membership still preferred.
    """
    if figure in source_figures:
        return True
    if not figure.startswith("percent:"):
        return False
    try:
        narrated = float(figure.split(":", 1)[1])
    except ValueError:
        return False
    for source in source_figures:
        if not source.startswith("percent:"):
            continue
        try:
            src = float(source.split(":", 1)[1])
        except ValueError:
            continue
        if abs(narrated - src) <= PERCENT_TOLERANCE_PP:
            return True
    return False


__all__ = [
    "PERCENT_TOLERANCE_PP",
    "_FIGURE_RE",
    "_figure_near_match",
    "_figures",
    "_normalize_figure",
]
