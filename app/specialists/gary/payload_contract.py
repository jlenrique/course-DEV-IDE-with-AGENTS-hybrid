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
        # Canonical-arc S3 (D4, 2026-07-07): the three shadow-parity context
        # keys the runner threads as CHARTERED runner context (F-802 option
        # (i)) — CD's committed styleguide_resolution block verbatim, the
        # sha256 of the directive bytes the gamma-settings parse read, and
        # the trial-start attestation digest (F-801: from trial-start.json).
        # Consumed by the observability-only parity audit in
        # generate_gamma_variants; never by dispatch composition.
        "cd_styleguide_resolution",
        "directive_digest",
        "directive_path",
        "double_dispatch",
        "export_dir",
        "gamma_settings",
        "input_text",
        "per_slide_directives",
        "prompt",
        "slides",
        "theme_id",
        "theme_limit",
        "trial_start_directive_digest",
    }
)

__all__ = ["CONSUMED_PAYLOAD_KEYS"]
