"""Tracy consumer fixture (Story 31-3 AC-T.6).

Minimal import-and-usage stub demonstrating how Story 28-2 (Tracy three-modes)
will dispatch based on :data:`COMPONENT_TYPE_REGISTRY` — given a
``component_type_ref``, look up the composite and act on its ``modality_refs``.

The ``demonstrate()`` callable at module scope is the loader entry point.
"""

from __future__ import annotations

from app.marcus.lesson_plan import (
    COMPONENT_TYPE_REGISTRY,
    get_component_type_entry,
)


def _dispatch_for_component_type(component_type_ref: str) -> tuple[str, ...]:
    """Return the modality tuple Tracy would enrich against."""
    entry = get_component_type_entry(component_type_ref)
    if entry is None:
        return ()
    return entry.modality_refs


def demonstrate() -> None:
    """Loader entry point. Invoked by test_consumer_fixtures_load."""
    # (1) Minimal composite — single modality.
    assert _dispatch_for_component_type("narrated-deck") == ("slides",)

    # (2) Multi-modality composite.
    assert _dispatch_for_component_type("motion-enabled-narrated-lesson") == (
        "slides",
        "blueprint",
    )

    # (3) Unknown component-type.
    assert _dispatch_for_component_type("nonexistent-composite") == ()

    # (4) Direct registry iteration works as well (public Mapping).
    assert len(COMPONENT_TYPE_REGISTRY) == 2
