from __future__ import annotations

import os
import time
from collections.abc import Callable
from typing import Any

import pytest

_PLACEHOLDER_SENTINELS = (
    "<placeholder>",
    "<your-instance>",
    "<your-data-center>",
    "sk-<placeholder>",
    "sk-substrate-no-real-key-do-not-invoke",
)


def _is_placeholder(value: str) -> bool:
    normalized = value.strip()
    if not normalized:
        return True
    return any(token in normalized for token in _PLACEHOLDER_SENTINELS)


@pytest.fixture
def env_value() -> Callable[..., str | dict[str, str]]:
    def _env_value(*names: str) -> str | dict[str, str]:
        resolved: dict[str, str] = {}
        for name in names:
            value = (os.environ.get(name) or "").strip()
            if _is_placeholder(value):
                pytest.skip(f"{name} not set in env")
            resolved[name] = value
        if len(names) == 1:
            return resolved[names[0]]
        return resolved

    return _env_value


@pytest.fixture
def timed_call() -> Callable[[Callable[[], Any]], tuple[Any, float]]:
    def _timed_call(fn: Callable[[], Any]) -> tuple[Any, float]:
        started = time.monotonic()
        result = fn()
        elapsed = time.monotonic() - started
        assert elapsed < 10, f"live smoke call exceeded 10s ({elapsed:.2f}s)"
        return result, elapsed

    return _timed_call


@pytest.fixture
def qualtrics_base_url(env_value: Callable[..., str | dict[str, str]]) -> str:
    preferred = (os.environ.get("QUALTRICS_BASE_URL") or "").strip()
    if preferred and not _is_placeholder(preferred):
        return preferred.rstrip("/")

    legacy = (os.environ.get("QUALTRICS_DATA_CENTER") or "").strip()
    if legacy and not _is_placeholder(legacy):
        return f"https://{legacy}.qualtrics.com"

    env_value("QUALTRICS_BASE_URL")
    raise AssertionError("unreachable")
