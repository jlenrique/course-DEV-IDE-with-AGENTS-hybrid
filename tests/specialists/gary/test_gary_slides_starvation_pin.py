"""PIN (taxonomy re-base live-path tranche, 2026-06-12): gary's fabricated
slide-01 roster is gone — behavior AND source (quinn_r PIN-AUD-2R precedent).
A dispatch with no slides refuses via the newly dispatch-family GaryActError
(error-pause, not crash), never invents a placeholder deck.
"""

from __future__ import annotations

import inspect

import pytest

from app.specialists.dispatch_errors import SpecialistDispatchError
from app.specialists.gary import _act as gary_act


def test_gary_empty_slides_refuses() -> None:
    with pytest.raises(gary_act.GaryActError) as excinfo:
        gary_act._slides({})
    assert excinfo.value.tag == "gamma.slides.starved"
    assert '"slide-01"' not in inspect.getsource(gary_act)


@pytest.mark.parametrize("payload", [{}, {"slides": []}, {"per_slide_directives": []}])
def test_gary_starvation_variants_all_refuse(payload: dict) -> None:
    # Pins _slides() directly. At the act() boundary an empty-slides payload
    # routes to the directive lane first and refuses there with
    # GammaDispatchError (missing-input) — also loud + recoverable, different
    # tag (edge-hunter note; routing-predicate cleanup queued at next touch).
    with pytest.raises(gary_act.GaryActError):
        gary_act._slides(payload)


def test_gary_real_roster_passes_through_unchanged() -> None:
    rows = [{"slide_id": "s1", "prompt": "p1"}, {"slide_id": "s2", "prompt": "p2"}]
    assert gary_act._slides({"slides": rows}) == rows


def test_gary_errors_are_dispatch_family() -> None:
    from app.specialists.gary.graph import ReceiptParseError

    for cls in (gary_act.GaryActError, ReceiptParseError):
        assert issubclass(cls, SpecialistDispatchError)
        assert issubclass(cls, RuntimeError)  # existing handlers preserved
