"""Irene consumer fixture (Story 31-3 AC-T.6).

Minimal import-and-usage stub demonstrating how Story 29-2 (Irene
diagnostician) will reference :data:`MODALITY_REGISTRY` to check the
validity of a ``PlanUnit.modality_ref`` value during diagnosis.

The ``demonstrate()`` callable at module scope is the loader entry point.
"""

from __future__ import annotations

from app.marcus.lesson_plan import get_modality_entry


def _check_modality_ref_validity(modality_ref: str) -> bool:
    """Return True iff the modality_ref is a key in the registry."""
    return get_modality_entry(modality_ref) is not None


def demonstrate() -> None:
    """Loader entry point. Invoked by test_consumer_fixtures_load."""
    # (1) Known modality — valid.
    assert _check_modality_ref_validity("slides") is True
    assert _check_modality_ref_validity("blueprint") is True

    # (2) Pending modality is still a registered key — Irene would accept it
    # as valid and let a separate layer decide whether to route.
    assert _check_modality_ref_validity("leader-guide") is True

    # (3) Unknown modality — Irene would flag this as a diagnosis error.
    assert _check_modality_ref_validity("unknown-modality") is False
    assert _check_modality_ref_validity("") is False
    assert _check_modality_ref_validity("SLIDES") is False
