"""Fixtures for the notifier test suite (Story 35.6). Helpers live in _helpers."""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

import pytest

from tests.notify._helpers import BASE_TIME, FakeApprise, ProjectionWriter


@pytest.fixture
def run_dir(tmp_path: Path) -> Path:
    d = tmp_path / "run"
    d.mkdir()
    return d


@pytest.fixture
def state_dir(tmp_path: Path) -> Path:
    return tmp_path / "notify-state"


@pytest.fixture
def writer(run_dir: Path) -> ProjectionWriter:
    return ProjectionWriter(run_dir)


@pytest.fixture
def fake_apprise() -> FakeApprise:
    return FakeApprise()


@pytest.fixture
def clock():
    """A steppable clock returning increasing tz-aware datetimes."""

    class Clock:
        def __init__(self) -> None:
            self.t = BASE_TIME

        def now(self) -> datetime:
            return self.t

        def advance(self, seconds: float) -> None:
            self.t = self.t + timedelta(seconds=seconds)

    return Clock()
