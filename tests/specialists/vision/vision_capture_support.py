"""Test-support helper for vision live-capture portability (carried-findings D-C2).

The runtime provider sets ``VisionProviderResponse.source_png_path`` ABSOLUTE
(``str(path)`` in ``perceive_png``) — correct at runtime, unportable in
committed fixtures. The capture harness in
``test_vision_live_roundtrip.py`` normalizes the recorded copy through
:func:`normalize_capture_response_paths` before writing it to
``tests/fixtures/vision/recordings/``. Runtime code stays untouched.
"""

from __future__ import annotations

from pathlib import Path


def normalize_capture_response_paths(response: dict, *, repo_root: Path) -> dict:
    """Normalize ``response['source_png_path']`` to repo-relative posix form.

    Mutates ``response`` IN PLACE and returns the same dict (capture-layer
    convenience; callers pass a fresh ``model_dump()`` dict, never the live
    response object).

    Both sides are ``resolve()``-d before ``relative_to`` so Windows
    drive-letter case / 8.3 aliases cannot produce a spurious mismatch.

    FAIL LOUD (party-ratified, Murat over warn-fallback): if the path cannot
    be expressed as a repo-relative posix path to a file WITHIN ``repo_root``
    — empty/whitespace raw value, the repo root itself, or a path that cannot
    be made repo-relative — raise ``ValueError``; such a recording must never
    be written.

    A missing ``source_png_path`` key is a no-op (nothing to normalize).
    """
    raw = response.get("source_png_path")
    if raw is None:
        return response

    if not str(raw).strip():
        # Path("").resolve() is the CWD — an empty raw value would otherwise
        # silently normalize to "." (or cwd-relative garbage).
        raise ValueError(
            f"capture portability violation: source_png_path {raw!r} is "
            "empty/whitespace. Committed vision recordings must hold "
            "repo-relative posix paths to a real png; refusing to write an "
            "unportable recording (carried-findings D-C2, FAIL LOUD)."
        )

    png = Path(raw).resolve()
    root = Path(repo_root).resolve()
    try:
        relative = png.relative_to(root)
    except ValueError as exc:
        # NOTE: not necessarily "outside the repo root" — an extended-length
        # (\\?\-prefixed) form of an in-repo path also lands here. Either way
        # the value cannot be made repo-relative, so it must not be written.
        raise ValueError(
            f"capture portability violation: source_png_path {raw!r} resolves to "
            f"{str(png)!r}, which cannot be made repo-relative to repo root "
            f"{str(root)!r}. Committed vision recordings must hold "
            "repo-relative posix paths; refusing to write an unportable "
            "recording (carried-findings D-C2, FAIL LOUD)."
        ) from exc

    value = relative.as_posix()
    if value in ("", "."):
        raise ValueError(
            f"capture portability violation: source_png_path {raw!r} normalizes "
            f"to {value!r} — the repo root itself, not a file within it; "
            "refusing to write an unportable recording (carried-findings D-C2, "
            "FAIL LOUD)."
        )

    response["source_png_path"] = value
    return response
