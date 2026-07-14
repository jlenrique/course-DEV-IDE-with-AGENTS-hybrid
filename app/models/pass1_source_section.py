"""Dual-identity authenticated source sections for Irene Pass-1."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass


def canonical_extracted_content_digest(value: str) -> str:
    """Digest the exact Texas section body under its extraction contract."""
    normalized = value.replace("\r\n", "\n").replace("\r", "\n").strip()
    return "sha256:" + hashlib.sha256(normalized.encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class Pass1AuthenticatedSourceSection:
    """One raw-source identity paired with one authenticated extracted body."""

    source_id: str
    source_content_digest: str
    extracted_content_digest: str
    body: str


__all__ = [
    "Pass1AuthenticatedSourceSection",
    "canonical_extracted_content_digest",
]
