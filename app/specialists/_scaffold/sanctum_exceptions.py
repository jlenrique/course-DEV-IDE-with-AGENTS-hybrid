"""Shared sanctum-related exceptions."""

from __future__ import annotations


class SanctumLockViolation(RuntimeError):  # noqa: N818
    """Raised when a populated sanctum lock baseline drifts."""


__all__ = ["SanctumLockViolation"]
