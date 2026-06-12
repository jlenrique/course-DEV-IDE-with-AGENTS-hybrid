"""Gary consumed-payload contract (S1, SCP 2026-06-11 segment-data-plane).

Declares every key Gary's act body reads from its envelope payload. The
manifest contract lockstep test (Ratchet-D) asserts that any manifest
dependency edge targeting gary uses ONLY keys declared here, and the S3
package builder's output keys must be a subset of this set — locking the
lesson-plan -> slide-briefs -> Gamma chain into one vocabulary.
"""

from __future__ import annotations

CONSUMED_PAYLOAD_KEYS: frozenset[str] = frozenset(
    {
        "additional_instructions",
        "directive_path",
        "double_dispatch",
        "export_dir",
        "input_text",
        "per_slide_directives",
        "prompt",
        "slides",
        "theme_id",
        "theme_limit",
    }
)

__all__ = ["CONSUMED_PAYLOAD_KEYS"]
