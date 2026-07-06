"""Canonical-arc S2 D5 — the F-403 variant-vocabulary lockstep pin.

F-403 (binding): the picker's `_VARIANT_IDS` and CD's `_PICK_VARIANT_VOCABULARY`
are two INDEPENDENT `{A, B}` constants. A production import between
`app.marcus.orchestrator.styleguide_picker` and `app.specialists.cd.graph` is
STRUCTURALLY FORBIDDEN (the S1 lint contract + the AST picker-boundary guard in
`tests/marcus/orchestrator/test_styleguide_picker.py` enforce it) — so the only
place the two constants may legally meet is a TEST. This file is that meeting
point: it imports BOTH (test-level imports are the chartered exception) and
pins their set equality so an unnoticed vocabulary drift fails loud here
instead of surfacing as a false S3 parity divergence.
"""

from __future__ import annotations

from app.marcus.orchestrator.styleguide_picker import _VARIANT_IDS
from app.specialists.cd.graph import _PICK_VARIANT_VOCABULARY


def test_variant_vocabularies_identical() -> None:
    # Lockstep pin, NOT a coupling: production code may not import across the
    # picker/CD boundary (F-403); this test is the sanctioned drift detector.
    assert set(_VARIANT_IDS) == set(_PICK_VARIANT_VOCABULARY) == {"A", "B"}
