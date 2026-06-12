"""Shared fail-loud reader: extracted corpus content for planner prompts.

Trial-3 cycle-2 content-plane root cause (2026-06-12): irene_pass1 and cd
received Texas's bundle *metadata* (paths, word counts) through the two
edges Ratchet-D had QUARANTINED as un-contracted — never the extracted
corpus text. With no source in sight, the planner LLMs confabulated a
plausible lesson plan from their reference docs' domain, and the §06→§07
chain faithfully rendered the wrong course. Absence of source content is
a contract violation, never a planning license (S0 fail-loud policy).

``SourceBundleError`` is a ``SpecialistDispatchError``: a failure here
error-pauses the trial for ``trial recover`` instead of killing the cycle.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from app.specialists.dispatch_errors import SpecialistDispatchError


class SourceBundleError(SpecialistDispatchError):
    """Raised when the extracted source corpus cannot be obtained."""


def read_extracted_source(payload: dict[str, Any]) -> str:
    """Resolve the Texas bundle referenced by ``payload`` and read extracted.md.

    The bundle reference may sit at the payload top level or inside any
    delivered upstream-output dict (``upstream_output``, ``source_bundle``,
    …) — whichever edge vocabulary the manifest used.
    """
    candidates: list[dict[str, Any]] = [payload]
    candidates.extend(
        value for value in payload.values() if isinstance(value, dict)
    )
    bundle_ref: Path | None = None
    for candidate in candidates:
        ref = candidate.get("bundle_reference")
        if isinstance(ref, str) and ref.strip():
            bundle_ref = Path(ref)
            break
    if bundle_ref is None:
        raise SourceBundleError(
            "no bundle_reference found in payload (top level or delivered "
            f"upstream outputs); payload keys={sorted(payload)}",
            tag="source.bundle.reference-missing",
        )
    extracted = bundle_ref / "extracted.md"
    if not extracted.is_file():
        raise SourceBundleError(
            f"bundle at {bundle_ref.as_posix()} has no extracted.md",
            tag="source.bundle.extracted-missing",
        )
    text = extracted.read_text(encoding="utf-8")
    if not text.strip():
        raise SourceBundleError(
            f"extracted.md at {extracted.as_posix()} is empty",
            tag="source.bundle.extracted-empty",
        )
    return text


__all__ = ["SourceBundleError", "read_extracted_source"]
