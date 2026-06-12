"""Shared base for typed specialist dispatch errors.

S4 part 2 (SCP 2026-06-11 segment-data-plane, Winston d.2 + Amelia trap 1):
the production runner catches this base to convert a transient dispatch
failure into an error-pause (run recoverable via ``trial recover``) instead
of letting it kill the whole trial cycle. The S0 fail-loud seams (gary
Gamma, texas bundle, kira Kling, vera/quinn_r sensory bridges, wanda
Wondercraft) all re-base their per-seam error classes here; each keeps its
own name because tests and call sites pin them individually.
"""

from __future__ import annotations


class SpecialistDispatchError(RuntimeError):  # noqa: N818
    """A typed, taggable specialist dispatch failure (S0 fail-loud policy)."""

    def __init__(self, message: str, *, tag: str) -> None:
        super().__init__(message)
        self.tag = tag


__all__ = ["SpecialistDispatchError"]
