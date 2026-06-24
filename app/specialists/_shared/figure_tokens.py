"""Shared numeric figure token extraction for narration/perception gates."""

from __future__ import annotations

import re

_FIGURE_RE = re.compile(
    r"\$\s*\d+(?:\.\d+)?(?:\s*(?:trillion|billion)\b|\s*[tb]\b)?"
    r"|\b\d+(?:\.\d+)?\s*%|\b\d+(?:\.\d+)?x\b",
    re.IGNORECASE,
)


def _figures(text: str) -> set[str]:
    return {_normalize_figure(match.group(0)) for match in _FIGURE_RE.finditer(text)}


def _normalize_figure(value: str) -> str:
    token = value.lower().replace(" ", "")
    if token.startswith("$"):
        number = float(re.search(r"\d+(?:\.\d+)?", token).group(0))  # type: ignore[union-attr]
        if "trillion" in token or token.endswith("t"):
            return f"money-trillion:{number:g}"
        if "billion" in token or token.endswith("b"):
            return f"money-trillion:{number / 1000.0:g}"
        return f"money-bare:{number:g}"
    if token.endswith("%"):
        return f"percent:{float(token[:-1]):g}"
    if token.endswith("x"):
        return f"multiple:{float(token[:-1]):g}"
    return token


__all__ = ["_FIGURE_RE", "_figures", "_normalize_figure"]
