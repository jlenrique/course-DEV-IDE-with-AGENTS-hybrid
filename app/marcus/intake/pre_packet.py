"""Pre-packet construction + emission — Marcus-Intake → Irene handoff at step 04/05.

Home of two Intake-side functions:

* :func:`prepare_irene_packet` (Story 30-2a, byte-identical lift) — pure
  file-I/O builder that reads bundle artifacts and writes
  ``irene-packet.md``. LOCKED at 30-2a; do not refactor.
* :func:`prepare_and_emit_irene_packet` (Story 30-2b — this landing) —
  wraps :func:`prepare_irene_packet` and, on success, hands off a
  ``pre_packet_snapshot`` :class:`EventEnvelope` to a caller-injected
  orchestrator dispatch callable.

Maya-facing note
----------------

Maya does not call this module. It is an internal bundle aggregator +
handoff emitter that produces the ``irene-packet.md`` artifact Irene
consumes at the step-04 → step-05 boundary, plus a ``pre_packet_snapshot``
log event that downstream fanout (Story 30-4) reconstructs Intake-era
context from.

Developer discipline note
-------------------------

* **30-2a (refactor-only lift — LOCKED):** :func:`prepare_irene_packet`
  body is byte-identical to the pre-30-2a CLI script at
  ``scripts/utilities/prepare-irene-packet.py``. 30-2b does not modify
  its signature, docstring, or body.
* **30-2b (this commit — emission feature):** adds
  :func:`prepare_and_emit_irene_packet` which wraps the 30-2a function,
  constructs the :class:`PrePacketSnapshotPayload` + :class:`EventEnvelope`,
  and hands off to a caller-injected ``dispatch`` callable. Intake does
  NOT import :class:`LessonPlanLog` or
  :func:`marcus.orchestrator.write_api.emit_pre_packet_snapshot`
  directly; the dependency-injection pattern preserves single-writer
  discipline and keeps Intake independently importable (R1 amendment 13).

Byte-identity invariant
-----------------------

The 30-1 Golden-Trace regression test at
``tests/test_marcus_golden_trace_regression.py`` pins the pre-refactor
envelope I/O against the committed fixture at
``tests/fixtures/golden_trace/marcus_pre_30-1/``. 30-2b adds a
log-write side effect but does NOT modify packet-file I/O — normalized
packet output remains byte-identical to the fixture. R1 ruling
amendment 12 (Murat RED binding PDG).

Lift origin
-----------

* Pre-30-2a location: ``scripts/utilities/prepare-irene-packet.py``
  (lines 18-75 of the pre-30-2a file).
* Lift commit: 30-2a (see Story
  ``_bmad-output/implementation-artifacts/30-2a-pre-packet-extraction-lift.md``).
* Emission feature: 30-2b (see Story
  ``_bmad-output/implementation-artifacts/30-2b-pre-packet-envelope-emission.md``).
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Final

from app.marcus.lesson_plan.events import EventEnvelope
from app.marcus.lesson_plan.log import (
    PRE_PACKET_SNAPSHOT_EVENT_TYPE,
    PrePacketSnapshotPayload,
    SourceRef,
)

__all__: Final[tuple[str, ...]] = (
    "prepare_and_emit_irene_packet",
    "prepare_irene_packet",
)

# Repo root derived from this module's location (<repo>/marcus/intake/pre_packet.py).
# Cwd-independent; mirrors the 31-2 LOG_PATH discipline (G6 MF-BH-1 precedent).
_REPO_ROOT: Final[Path] = Path(__file__).resolve().parents[2]


def prepare_irene_packet(
    bundle_dir: Path,
    run_id: str,
    output_path: Path,
) -> dict[str, Any]:
    """Generate irene-packet.md from bundle artifacts."""
    # Read inputs
    extracted_md = bundle_dir / "extracted.md"
    metadata_json = bundle_dir / "metadata.json"
    operator_directives = bundle_dir / "operator-directives.md"
    ingestion_receipt = bundle_dir / "ingestion-quality-gate-receipt.md"

    if not extracted_md.exists():
        raise FileNotFoundError(f"extracted.md not found in {bundle_dir}")
    if not metadata_json.exists():
        raise FileNotFoundError(f"metadata.json not found in {bundle_dir}")
    if not operator_directives.exists():
        raise FileNotFoundError(f"operator-directives.md not found in {bundle_dir}")

    extracted_content = extracted_md.read_text(encoding="utf-8")
    metadata = json.loads(metadata_json.read_text(encoding="utf-8"))
    directives_content = operator_directives.read_text(encoding="utf-8")

    ingestion_content = ""
    if ingestion_receipt.exists():
        ingestion_content = ingestion_receipt.read_text(encoding="utf-8")

    # Build packet sections
    packet_sections = [
        f"# Irene Packet for {run_id}",
        "",
        "## Source Bundle Summary",
        f"- Primary source: {metadata.get('primary_source', 'unknown')}",
        f"- Total sections: {metadata.get('total_sections', 'unknown')}",
        f"- Extraction confidence: {metadata.get('overall_confidence', 'unknown')}",
        "",
        "## Operator Directives",
        directives_content,
        "",
        "## Ingestion Quality Receipt",
        ingestion_content,
        "",
        "## Extracted Content",
        extracted_content,
    ]

    packet_content = "\n".join(packet_sections)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(packet_content, encoding="utf-8")

    return {
        "packet_path": str(output_path),
        "sections": len(packet_sections),
        "has_directives": bool(directives_content.strip()),
        "has_ingestion_receipt": bool(ingestion_content.strip()),
    }


# ---------------------------------------------------------------------------
# 30-2b: emission wiring
# ---------------------------------------------------------------------------


def _compute_sha256_hex(data: bytes) -> str:
    """Return the sha256 hex digest of ``data``."""
    return hashlib.sha256(data).hexdigest()


def _to_repo_relative_posix(path: Path) -> str:
    """Convert ``path`` to a POSIX-style repo-relative string.

    31-2's :class:`PrePacketSnapshotPayload.pre_packet_artifact_path`
    validator rejects absolute paths and ``..`` traversal segments, so
    this helper resolves ``path`` and strips the repo-root prefix. Uses
    POSIX separators so the payload is cross-platform deterministic
    (Windows backslashes would fail the validator).
    """
    resolved = path.resolve()
    try:
        relative = resolved.relative_to(_REPO_ROOT)
    except ValueError as exc:
        raise ValueError(
            f"pre-packet artifact path must live under the repo root "
            f"({_REPO_ROOT}); got {resolved}"
        ) from exc
    return relative.as_posix()


def _build_sme_refs(
    metadata: dict[str, Any],
    bundle_dir: Path,
) -> list[SourceRef]:
    """Construct ``sme_refs`` from bundle metadata (AC-B.5 branch matrix).

    Two branches:
    * ``metadata["sme_refs"]`` present and non-empty → parse each dict into
      a :class:`SourceRef`.
    * absent → synthesize a single-element list from ``primary_source``;
      ``content_digest`` is computed from ``extracted.md`` bytes because
      the metadata lacks an explicit digest.
    """
    raw_refs = metadata.get("sme_refs")
    if raw_refs:
        return [
            SourceRef(
                source_id=entry["source_id"],
                path=entry.get("path"),
                content_digest=entry["content_digest"],
            )
            for entry in raw_refs
        ]

    primary_source = metadata.get("primary_source", "unknown")
    extracted_bytes = (bundle_dir / "extracted.md").read_bytes()
    return [
        SourceRef(
            source_id=str(primary_source),
            path=None,
            content_digest=_compute_sha256_hex(extracted_bytes),
        )
    ]


def prepare_and_emit_irene_packet(
    bundle_dir: Path,
    run_id: str,
    output_path: Path,
    *,
    dispatch: Callable[[EventEnvelope], None],
    plan_revision: int,
) -> dict[str, Any]:
    """Build the Irene packet AND emit the ``pre_packet_snapshot`` event.

    Story 30-2b emission surface. The orchestration:

    1. :func:`prepare_irene_packet` — byte-identical packet-file build.
       Raises :class:`FileNotFoundError` on missing required inputs;
       propagates WITHOUT emitting (AC-B.4 zero-emission-on-failure).
    2. Payload construction — :class:`PrePacketSnapshotPayload` built
       from bundle metadata + the packet result.
    3. Envelope construction — :class:`EventEnvelope` with fresh UUID4
       ``event_id`` (auto-factory), timezone-aware ``timestamp``
       (29-1 precedent), caller-supplied ``plan_revision``, and
       ``event_type="pre_packet_snapshot"``.
    4. ``dispatch(envelope)`` — caller-injected callable routes to the
       Orchestrator write API. Intake does NOT import
       :mod:`marcus.orchestrator.write_api` directly.

    Args:
        bundle_dir: Directory containing the source bundle (same as
            :func:`prepare_irene_packet`).
        run_id: Run identifier.
        output_path: Destination for the generated ``irene-packet.md``.
        dispatch: Callable that receives the built :class:`EventEnvelope`
            and routes it to the Orchestrator write API. Production
            callers pass
            :func:`marcus.orchestrator.dispatch.dispatch_intake_pre_packet`.
            Tests may pass a stub that captures envelopes for inspection.
        plan_revision: Lesson plan revision at snapshot time. Pre-plan
            emissions (typical for the step-04 → step-05 handoff before
            any plan exists) pass ``0``.

    Returns:
        The same dict :func:`prepare_irene_packet` returns; no new keys.

    Raises:
        FileNotFoundError: Propagated from :func:`prepare_irene_packet`
            when a required bundle file is missing. Emission does NOT
            occur on this path.
        pydantic.ValidationError: If the metadata produces an invalid
            :class:`PrePacketSnapshotPayload` (e.g., ``sme_refs`` entries
            missing required fields, absolute ``pre_packet_artifact_path``,
            empty digests). Emission does NOT occur on this path.
    """
    # Step 1: build the packet file (byte-identical 30-2a behavior).
    # Any FileNotFoundError here propagates WITHOUT emission (AC-B.4).
    packet_result = prepare_irene_packet(bundle_dir, run_id, output_path)

    # Step 2: build the PrePacketSnapshotPayload.
    # Metadata read is deterministic — matches prepare_irene_packet's ordering.
    extracted_bytes = (bundle_dir / "extracted.md").read_bytes()
    metadata_bytes = (bundle_dir / "metadata.json").read_bytes()
    directives_bytes = (bundle_dir / "operator-directives.md").read_bytes()

    # Fixed-order canonical concatenation (documented invariant).
    ingestion_digest = _compute_sha256_hex(
        extracted_bytes + metadata_bytes + directives_bytes
    )
    step_03_checksum = _compute_sha256_hex(extracted_bytes)
    metadata = json.loads(metadata_bytes.decode("utf-8"))
    sme_refs = _build_sme_refs(metadata, bundle_dir)
    artifact_path = _to_repo_relative_posix(Path(packet_result["packet_path"]))

    payload = PrePacketSnapshotPayload(
        sme_refs=sme_refs,
        ingestion_digest=ingestion_digest,
        pre_packet_artifact_path=artifact_path,
        step_03_extraction_checksum=step_03_checksum,
    )

    # Step 3: build the EventEnvelope.
    envelope = EventEnvelope(
        timestamp=datetime.now(tz=UTC),
        plan_revision=plan_revision,
        event_type=PRE_PACKET_SNAPSHOT_EVENT_TYPE,
        payload=payload.model_dump(mode="json"),
    )

    # Step 4: hand off to the Orchestrator dispatch seam.
    dispatch(envelope)

    return packet_result
