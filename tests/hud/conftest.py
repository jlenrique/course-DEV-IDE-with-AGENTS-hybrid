"""Shared pytest fixtures for the HUD server/reader tests (Story 35.4).

Builder helpers live in ``tests.hud._helpers`` (imported directly by test
modules); this file holds only the fixtures.
"""

from __future__ import annotations

import uuid
from pathlib import Path

import pytest


@pytest.fixture
def run_dir(tmp_path: Path) -> Path:
    d = tmp_path / "run"
    d.mkdir()
    return d


@pytest.fixture
def bound_trial_id() -> uuid.UUID:
    return uuid.UUID("11111111-1111-4111-8111-111111111111")
