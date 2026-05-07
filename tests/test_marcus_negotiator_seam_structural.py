"""Story 30-3a — NEGOTIATOR_SEAM structural-marker upgrade.

AC-T.9 — NEGOTIATOR_SEAM upgraded from 30-1 string sentinel to a
typed :class:`NegotiatorSeam` structural marker while preserving
``str(NEGOTIATOR_SEAM) == "marcus-negotiator"`` for 30-1's grep-
discoverable sentinel contract.
"""

from __future__ import annotations

from app.marcus.orchestrator import NEGOTIATOR_SEAM, NegotiatorSeam


def test_negotiator_seam_is_structural_marker_with_string_backcompat() -> None:
    """AC-T.9 — NegotiatorSeam instance; structural fields present; str backcompat."""
    # Instance check — upgraded from string sentinel.
    assert isinstance(NEGOTIATOR_SEAM, NegotiatorSeam)

    # 30-1 grep-discoverable sentinel contract preserved.
    assert str(NEGOTIATOR_SEAM) == "marcus-negotiator"

    # Structural fields exist with expected types + defaults.
    assert NEGOTIATOR_SEAM.pending_queue == ()
    assert NEGOTIATOR_SEAM.dialogue_history == ()
    assert NEGOTIATOR_SEAM.active_loop is False

    # Instantiable with explicit values.
    loaded = NegotiatorSeam(
        pending_queue=("u1", "u2"),
        dialogue_history=(("maya-prompt", "should we keep u1?"),),
        active_loop=True,
    )
    assert loaded.pending_queue == ("u1", "u2")
    assert loaded.dialogue_history == (("maya-prompt", "should we keep u1?"),)
    assert loaded.active_loop is True
    # Backward-compat __str__ on any instance.
    assert str(loaded) == "marcus-negotiator"
