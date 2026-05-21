"""Negotiator seam named contract (AC-T.9; updated by 30-3a).

Pins the seam contract after 30-3a's structural upgrade:
* ``NEGOTIATOR_SEAM`` is an instance of :class:`NegotiatorSeam`.
* ``str(NEGOTIATOR_SEAM) == "marcus-negotiator"`` preserves 30-1's
  grep-discoverable sentinel contract.
* Seam documented in ``marcus/orchestrator/__init__.py`` docstring
  (title may vary post-30-3a).
"""

from __future__ import annotations


def test_negotiator_seam_str_backcompat() -> None:
    """AC-T.9 — ``str(NEGOTIATOR_SEAM) == "marcus-negotiator"`` (30-1 grep contract)."""
    from app.marcus.orchestrator import NEGOTIATOR_SEAM

    assert str(NEGOTIATOR_SEAM) == "marcus-negotiator"


def test_negotiator_seam_is_structural_marker() -> None:
    """AC-T.9 (30-3a) — NEGOTIATOR_SEAM upgraded to :class:`NegotiatorSeam`."""
    from app.marcus.orchestrator import NEGOTIATOR_SEAM, NegotiatorSeam

    assert isinstance(NEGOTIATOR_SEAM, NegotiatorSeam)


def test_orchestrator_docstring_names_the_seam() -> None:
    """AC-T.9 — orchestrator docstring names the negotiator seam somewhere."""
    import app.marcus.orchestrator as orchestrator
    docstring = orchestrator.__doc__ or ""
    assert "negotiator" in docstring.lower(), (
        "marcus/orchestrator/__init__.py docstring must name the negotiator "
        "seam so 30-3b's dev agent discovers it via grep."
    )
