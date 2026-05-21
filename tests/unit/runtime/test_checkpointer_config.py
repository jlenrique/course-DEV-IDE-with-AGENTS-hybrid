"""`resolve_database_url` unit test — no Postgres connection (AC-1.5-A).

Isolates the env-var resolution from the `AsyncPostgresSaver` connect path so
DATABASE_URL presence/absence is covered without a live Postgres dependency.
"""

from __future__ import annotations

import pytest

from app.runtime.checkpointer import CheckpointerConfigError, resolve_database_url


def test_resolve_raises_when_env_unset(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    with pytest.raises(CheckpointerConfigError, match="DATABASE_URL env var not set"):
        resolve_database_url()


def test_resolve_returns_env_when_set(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/db")
    assert resolve_database_url() == "postgresql://user:pass@localhost:5432/db"
