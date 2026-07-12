"""Regression: `_normalize_figure` must not crash on non-numeric tokens.

Surfaced by the 35.7 HUD re-witness run at node 08: a research supplement
carried a DOI/retrieval reference ending in "x"
(``retrieval:scite:10.1057/s41599-024-03196-x``), and the ``token.endswith("x")``
multiple-parser did ``float(token[:-1])`` → ValueError, crashing the numeric-
provenance audit (and the walk) unmapped. A token that merely ends in %/x or
starts with $ but is not numeric must fall through to an opaque token.
"""

from __future__ import annotations

import pytest

from app.specialists._shared.figure_tokens import _normalize_figure


@pytest.mark.parametrize(
    ("token", "expected"),
    [
        # the crashing case: DOI/retrieval reference ending in "x" -> opaque
        ("retrieval:scite:10.1057/s41599-024-03196-x", "retrieval:scite:10.1057/s41599-024-03196-x"),
        ("doi:10.1000/foo-x", "doi:10.1000/foo-x"),
        ("$notanumber", "$notanumber"),
        ("abc%", "abc%"),
        # real figures still normalize
        ("3x", "multiple:3"),
        ("2.5x", "multiple:2.5"),
        ("10%", "percent:10"),
        ("$5billion", "money-trillion:0.005"),
        ("plainword", "plainword"),
    ],
)
def test_normalize_figure_never_crashes_on_non_numeric(token: str, expected: str) -> None:
    assert _normalize_figure(token) == expected
