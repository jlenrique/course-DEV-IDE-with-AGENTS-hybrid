from __future__ import annotations

import json

import pytest

from app.models.state.cache_state import CacheState
from app.models.state.run_state import RunState
from app.specialists.irene_pass1.graph import ModeMismatchError, _receive


def test_pass2_envelope_routed_to_pass1_raises_mode_mismatch() -> None:
    state = RunState(
        graph_version="v0.1-stub",
        cache_state=CacheState(
            cache_prefix=json.dumps({"mode": "pass-2", "topic": "cells"})
        ),
    )

    with pytest.raises(ModeMismatchError):
        _receive(state)


def test_pass1_mode_is_accepted() -> None:
    state = RunState(
        graph_version="v0.1-stub",
        cache_state=CacheState(
            cache_prefix=json.dumps({"mode": "pass-1", "topic": "cells"})
        ),
    )
    assert _receive(state) == {}
