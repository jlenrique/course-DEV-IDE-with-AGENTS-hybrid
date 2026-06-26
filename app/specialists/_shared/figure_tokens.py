"""Shared numeric figure token extraction for narration/perception gates."""

from __future__ import annotations

import re

_FIGURE_RE = re.compile(
    r"\$\s*\d+(?:\.\d+)?(?:\s*(?:trillion|billion)\b|\s*[tb]\b)?"
    r"|\b\d+(?:\.\d+)?\s*%|\b\d+(?:\.\d+)?x\b",
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
    r"\$\s*(\d+(?:\.\d+)?)\s*"
    r"(?:to|through|and|[-–—])\s*"
    r"\$\s*(\d+(?:\.\d+)?)\s*(trillion|billion|[tb])\b",
    re.IGNORECASE,
)


def _figures(text: str) -> set[str]:
    tokens: set[str] = set()
    consumed: list[tuple[int, int]] = []
    for match in _RANGE_RE.finditer(text):
        unit = match.group(3).lower()
        tokens.add(_normalize_money(float(match.group(1)), unit))
        tokens.add(_normalize_money(float(match.group(2)), unit))
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
    token = value.lower().replace(" ", "")
    if token.startswith("$"):
        number = float(re.search(r"\d+(?:\.\d+)?", token).group(0))  # type: ignore[union-attr]
        if "trillion" in token or token.endswith("t"):
            unit: str | None = "trillion"
        elif "billion" in token or token.endswith("b"):
            unit = "billion"
        else:
            unit = None
        return _normalize_money(number, unit)
    if token.endswith("%"):
        return f"percent:{float(token[:-1]):g}"
    if token.endswith("x"):
        return f"multiple:{float(token[:-1]):g}"
    return token


__all__ = ["_FIGURE_RE", "_figures", "_normalize_figure"]
