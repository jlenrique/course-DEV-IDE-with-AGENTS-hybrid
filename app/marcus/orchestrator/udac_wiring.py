"""UDAC v1 orchestrator wiring — the gate WRITER + the dispatch-site READER.

Per §F.2 (M-1, load-bearing): the index *assembly* is a GATE-crossing side-effect
(an asset is ratified only when the operator clears its gate), so the writer fires
in BOTH walk bodies (start reaches G1; continuation owns G2B+), exactly where
``storyboard_publisher`` / ``chooser_publisher`` / ``run_g0_enrichment`` already
sit — idempotent + monotonic. The READER (``resolve_asset`` + the fail-loud check)
lives at the SHARED dispatch site (``_dispatch_specialist_at_node``), walk-invariant.

All RAI MODEL logic + the resolver live in the NEUTRAL module
``app.marcus.lesson_plan.run_asset_index`` (RESOLVE-ASSET-LIVES-NEUTRAL, M3-clean);
this orchestrator module only owns the gate side-effect + the disk-primary I/O +
the env feature-flag (default OFF → existing pipeline byte-identical).

Disk-primary (§F.1 / M-3 / RAI-REHYDRATE-RECONCILE): ``<run_dir>/run-asset-index.json``
is the SSOT; the gate writer LOADS the on-disk RAI, reconciles monotonically, and
writes it back — so a continuation/recover walk that re-crosses a gate rehydrates
the prior ratified_at rather than re-stamping (both-walks parity, M-5). The
run-state pointer-mirror (§F.1) is a v1 simplification: disk-primary +
rehydrate-from-disk gives the same survives-cold-resume guarantee without touching
``RunState`` (Contract M1) — see the dev report for the bounded deviation note.
"""

from __future__ import annotations

import json
import logging
import os
from datetime import UTC, datetime
from pathlib import Path

from app.marcus.lesson_plan.run_asset_index import (
    CONSUMER_REGISTRY,
    GATE_ASSET_MAP,
    AssetResolutionError,
    AuthorityStatus,
    ResolvedAsset,
    RunAssetIndex,
    load_rai,
    recompute_digest_from_disk,
    resolve_asset,
    write_rai,
)

logger = logging.getLogger(__name__)

MARCUS_UDAC_ACTIVE_ENV = "MARCUS_UDAC_ACTIVE"


def udac_active() -> bool:
    """Return True iff UDAC v1 enforcement is woken (env toggle; default OFF).

    Default OFF keeps every existing trial flow byte-identical: the gate writer
    produces no RAI and the dispatch reader is a no-op.
    """
    return os.environ.get(MARCUS_UDAC_ACTIVE_ENV, "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def _derived_from(asset_id: str, asset_path: Path) -> str | None:
    """Best-effort TX-4 trust-chain: read the corpus_fingerprint a structured
    asset records, if present (never raises — provenance is advisory metadata)."""
    if asset_id != "g0-enrichment":
        return None
    try:
        payload = json.loads(asset_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    fp = payload.get("corpus_fingerprint") if isinstance(payload, dict) else None
    return str(fp) if fp else None


def record_gate_ratification(
    *,
    gate_code: str | None,
    run_dir: Path,
) -> RunAssetIndex | None:
    """Mark the gate's assets ratified — a both-walks gate side-effect (M-1).

    Disk-primary + rehydrate-then-reconcile-monotonic (M-3): loads the on-disk RAI,
    recomputes each mapped asset's digest FROM DISK (TX-5), stamps it ratified off
    ``gate_code`` (== ``last_gate_crossed``), and atomically writes the RAI back. A
    no-op when UDAC is OFF, the gate maps to no asset, or no mapped asset has landed
    on disk yet.

    OWN-GATE RE-PIN vs CONSUMER-STALE (review F1). When a mapped asset already has an
    entry and its on-disk digest DIVERGES, this is the asset's OWN ratifying gate
    re-pinning a legitimately current artifact (e.g. a recover re-cross after the
    one-process ``build_enrichment_result`` re-froze ``g0-enrichment.json``, or an
    additive P2/P3 layer) — so it is ADDITIVE GROWTH: ``repin_additive`` bumps the
    revision + re-pins ``{digest, ratified_at}``, NEVER a stale raise. Stale/raise
    semantics belong ONLY to a CONSUMER resolving against an older pin
    (``resolve_consumed_assets``), never to the producing gate.

    CRASH-PROOF (review F1): the gate writer is wired in BOTH walk bodies OUTSIDE the
    dispatch ``except SpecialistDispatchError`` channel, so it must NEVER raise. Any
    per-asset failure (corrupt/torn file mid-write, a corrupt on-disk RAI) is logged
    and SKIPPED — fail-loud is the CONSUMER's job, not the recorder's. The walk is
    never crashed by recording.
    """
    if not udac_active() or not gate_code:
        return None
    specs = GATE_ASSET_MAP.get(gate_code)
    if not specs:
        return None

    try:
        index = load_rai(run_dir) or RunAssetIndex()
    except AssetResolutionError as exc:
        # A corrupt on-disk RAI must not crash the recording side-effect; leave it
        # for the consumer guard to fail-loud on. Do NOT overwrite (avoid data loss).
        logger.warning("udac: skipping gate %s recording — RAI unreadable: %s", gate_code, exc)
        return None

    now = datetime.now(UTC)
    changed = False
    for spec in specs:
        asset_path = run_dir / spec.rel_path
        if not asset_path.is_file():
            # Asset for this gate not produced (optional / flag-off producer);
            # not ratified — never fabricate an entry.
            continue
        try:
            existing = index.get(spec.asset_id)
            if existing is None:
                index.mark_ratified(
                    asset_id=spec.asset_id,
                    path=spec.rel_path,
                    digest=recompute_digest_from_disk(asset_path, spec.digest_algo),
                    digest_algo=spec.digest_algo,
                    ratified_at=now,
                    produced_by_node=gate_code,
                    revision=0,
                    derived_from=_derived_from(spec.asset_id, asset_path),
                )
                changed = True
            else:
                # OWN-GATE additive re-pin: bumps revision iff the artifact grew;
                # an unchanged artifact is an idempotent no-op preserving ratified_at.
                before_rev = existing.revision
                entry = index.repin_additive(
                    spec.asset_id,
                    run_dir=run_dir,
                    ratified_at=now,
                    produced_by_node=gate_code,
                )
                if entry.revision != before_rev:
                    changed = True
        except AssetResolutionError as exc:
            # Corrupt/torn asset mid-write etc. — never crash the recorder.
            logger.warning(
                "udac: skipping asset %s at gate %s — %s", spec.asset_id, gate_code, exc
            )
            continue

    if not changed:
        # No new ratification → do NOT reopen the write window (Blind-F2).
        return index if index.entries else None
    write_rai(run_dir, index)
    logger.info(
        "udac: recorded gate %s ratification → RAI now indexes %d asset(s)",
        gate_code,
        len(index.entries),
    )
    return index


def resolve_consumed_assets(
    *,
    specialist_id: str,
    run_dir: Path,
) -> dict[str, ResolvedAsset] | None:
    """Fail-loud dispatch guard for a consumer's declared assets (M-4 / MT-3).

    For each asset the consumer declares as ``used`` that the RAI marks RATIFIED
    (the consumer is downstream of ``produced_by_node`` by construction of the
    linear walk), ``resolve_asset`` recomputes the digest FROM DISK and RAISES
    :class:`AssetResolutionError` on a missing/stale ratified asset — which the
    runner's existing ``except SpecialistDispatchError`` at the shared dispatch
    site routes through ``_pause_at_error`` (no parallel channel). Not-yet-ratified
    assets are the provisional window → no enforcement (the existing fail-soft
    loaders serve them). Returns the resolved views or ``None`` (the view is
    discarded by the guard in v1 — see ``ResolvedAsset``; payload injection deferred).

    RESIDUAL (review F4, accepted for v1): the guard keys off RAI ``authority_status``,
    so a consumer requiring an asset whose ``produced_by_node`` gate HAS crossed but
    whose file never reached the RAI (gate-crossed-but-asset-not-flushed) fails OPEN
    rather than loud. Making that path fail-loud needs gate-position tracking at the
    dispatch site (deliberately avoided in v1). Filed as
    ``udac-v1-fail-loud-on-gate-crossed-absent-asset`` (deferred inventory); F3
    (ratify on every gate-crossing branch) reduces the surface in the interim.
    """
    if not udac_active():
        return None
    declaration = CONSUMER_REGISTRY.get(specialist_id)
    if declaration is None:
        return None
    index = load_rai(run_dir)
    if index is None:
        return None  # no RAI yet → provisional window, nothing ratified to guard
    resolved: dict[str, ResolvedAsset] = {}
    for asset_id in declaration.required_assets():
        entry = index.get(asset_id)
        if entry is None or entry.authority_status is not AuthorityStatus.RATIFIED:
            continue  # provisional window for this asset → no fail-loud enforcement
        resolved[asset_id] = resolve_asset(
            index, asset_id, run_dir=run_dir, require_ratified=True
        )
    return resolved or None


__all__ = [
    "MARCUS_UDAC_ACTIVE_ENV",
    "record_gate_ratification",
    "resolve_consumed_assets",
    "udac_active",
]
