"""Leg-4 UDAC anti-tautology broken-asset HALT driver — REWIND-RECOVER a golden run
through the REAL production_runner CONTINUATION walk to prove the fail-loud
Universal Downstream Asset Contract (UDAC) guard.

WHAT THIS PROVES (Murat's done-signal bar)
-------------------------------------------
With ``MARCUS_UDAC_ACTIVE=1`` and a Run Asset Index (RAI) that ratifies
``g0-enrichment`` at its real on-disk digest, a *content-mutated*
``g0-enrichment.json`` raises ``AssetResolutionError(tag="udac.asset-stale")`` at
the single shared dispatch site
(``production_runner._dispatch_specialist_at_node``, ~line 1847) BEFORE the
g0-enrichment CONSUMER ``gary`` (node ``07``) is invoked — landing in the
runner-emitted ``error-pause.json``. A discriminating CONTROL (identical recover,
identical RAI, NO corruption) sails PAST the guard to the next dispatch/gate. The
halt is DIGEST-based (present-on-disk but mutated → stale), not presence-based, and
happens at $0 (no gpt/ElevenLabs spend, zero mp3/wav).

CHOSEN RECOVER-POINT + CONSUMER (see the report for the tradeoff)
    Golden 8d819b8d paused at node ``07E`` (kira, idx 30, tag kira.motion-plan.empty,
    last_gate_crossed=G2C). The g0-enrichment USED consumers (CONSUMER_REGISTRY) are
    ``gary`` (node 07, idx 23 — PAID Gamma), ``irene`` (node 08, idx 33 — PAID gpt)
    and ``workbook`` (node 07W — DROPPED by production_default composition; and its
    dispatched id "workbook_producer" is not even a registry key, so its UDAC guard
    never fires — not viable).
    We choose ``gary``. irene was REJECTED: it hard-projects
    ``perception_artifacts<-vision`` (node 07G/idx 32, never run in the golden), and
    re-entering directly at irene makes the dispatch adapter raise an UNCAUGHT
    ``ProductionDispatchAdapterError`` (a plain RuntimeError, NOT a
    SpecialistDispatchError → escapes ``_pause_at_error``) BEFORE irene's gpt call —
    so the CONTROL arm would crash, not sail. gary's ONLY projections come from
    ``package_builder@06`` (present in the golden), so its CONTROL dispatches a real
    paid Gamma call cleanly. We REPOSITION the recover point directly to node ``07``
    (gary, idx 23) and DROP the golden's gary@07 contribution so first-wins
    re-dispatches it: the UDAC guard fires immediately at gary's dispatch with NOTHING
    run before it → genuine "$0 before a PAID Gamma call".

MECHANISM (rewind-recover of a COPY; golden 8d819b8d is NEVER touched)
    1. Copy golden run dir -> state/config/runs/<NEW_TRIAL>/.
    2. Surgically rewrite trial-id fields in run.json + error-pause.json (NOT a
       blanket text replace: contribution OUTPUTS embed the golden UUID and each
       output_digest is hard-validated on load — we touch only non-digest id fields
       + runner directive/bundle paths, leaving every contribution byte-identical).
    3. Reposition error-pause.json to re-enter at node ``07`` (gary): set
       node_index = composed-manifest index of "07", node_id="07",
       specialist_id="gary", and DROP the golden's gary@07 contribution from the
       run.json envelope so first-wins re-dispatches gary. last_gate_crossed stays
       G2C (maps to no RAI asset → the entry-time ratify is a no-op).
    4. MINT the RAI on the CLEAN g0-enrichment.json via
       udac_wiring.record_gate_ratification(gate_code="G0E", run_dir=new_dir) with
       MARCUS_UDAC_ACTIVE=1 — pins g0-enrichment RATIFIED at its real disk digest.
    5a. --halt  --live: CORRUPT g0-enrichment.json (add a key; still valid JSON so it
        is a DIGEST mismatch TAG_STALE, not a parse-failure TAG_CORRUPT) then
        recover_production_trial(max_specialist_calls=1). Assert the runner-emitted
        error-pause.json carries tag=udac.asset-stale at node 07/gary, $0 spend.
    5b. --control --live: identical recover WITHOUT corruption. Assert the recover
        does NOT yield a udac.asset-stale halt (guard passed → gary re-dispatches a
        real paid Gamma call and the walk advances to the next gate).
    6. Offline (--build / --halt / --control / --all WITHOUT --live): prepare + mint
       the RAI + validate the plumbing (copy loads, RAI mints with a real disk
       digest, resolve_consumed_assets(gary) PASSES on the clean file and RAISES
       tag=udac.asset-stale on a temp-corrupted-then-restored file) WITHOUT invoking
       the live recover / any live API.

USAGE
    python scratchpad/leg4_udac_halt_driver.py --build
    python scratchpad/leg4_udac_halt_driver.py --all
    python scratchpad/leg4_udac_halt_driver.py --halt --live      [--trial-id UUID]
    python scratchpad/leg4_udac_halt_driver.py --control --live   [--trial-id UUID]

DO NOT commit / push. --live spends a single gpt narration call ONLY on the control
arm; the halt arm is $0.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import time
import traceback
from pathlib import Path
from uuid import UUID, uuid4

REPO = Path(r"C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS-hybrid")
RUNS_ROOT_REL = Path("state/config/runs")
RUNS_ROOT_ABS = REPO / RUNS_ROOT_REL
GOLDEN_TRIAL = "8d819b8d-01dd-4ed5-a07d-12c31d764d9b"
GOLDEN_DIR = RUNS_ROOT_ABS / GOLDEN_TRIAL

# The chosen g0-enrichment consumer + its manifest node (see module docstring).
# gary (node 07, PAID Gamma) is chosen over irene (node 08, PAID gpt): irene hard-
# projects perception_artifacts<-vision (node 07G, never run in the golden), and the
# dispatch adapter raises an UNCAUGHT ProductionDispatchAdapterError (a plain
# RuntimeError, NOT a SpecialistDispatchError -> escapes _pause_at_error) before
# irene's gpt call -> the CONTROL arm would crash rather than sail. gary's ONLY
# projections come from package_builder@06 (present in the golden) so its CONTROL
# dispatches cleanly; gary already has a contribution, so we DROP it and first-wins
# re-dispatches it. See the report for the full tradeoff.
CONSUMER_SPECIALIST_ID = "gary"
CONSUMER_NODE_ID = "07"
ASSET_ID = "g0-enrichment"
ASSET_REL_PATH = "g0-enrichment.json"
RATIFYING_GATE = "G0E"

sys.path.insert(0, str(REPO))


def log(*a: object) -> None:
    print(f"[{time.strftime('%H:%M:%S')}]", *a, flush=True)


# ---------------------------------------------------------------------------
# env / key handling (mirrors the leg-2 driver's sk-subst sentinel gotcha fix)
# ---------------------------------------------------------------------------


def _load_env_override(require_live: bool) -> dict[str, str]:
    report: dict[str, str] = {}
    try:
        os.environ.pop("OPENAI_API_KEY", None)
        from dotenv import load_dotenv  # type: ignore

        load_dotenv(REPO / ".env", override=True)
        report["dotenv_loaded"] = "yes"
    except Exception as exc:  # noqa: BLE001
        report["dotenv_loaded"] = f"no ({type(exc).__name__}: {exc})"
    if require_live:
        key = os.environ.get("OPENAI_API_KEY", "")
        assert key.startswith("sk-"), (
            "live OPENAI_API_KEY not loaded (must start with sk-); the dispatch "
            "branch that hosts the UDAC guard is gated on _has_live_openai()"
        )
    return report


def _mask(val: str | None) -> str:
    if not val:
        return "ABSENT"
    v = val.strip()
    return f"present(len={len(v)}, {v[:6]}…{v[-4:]})" if len(v) > 10 else "present(short)"


# ---------------------------------------------------------------------------
# composed-manifest index lookup (robust to composition reindexing)
# ---------------------------------------------------------------------------


def _composed_node_index(node_id: str) -> tuple[int, str | None]:
    from app.marcus.orchestrator.production_runner import (  # type: ignore
        compose_manifest,
        load_manifest,
    )

    try:
        from app.models.runtime.component_selection import ComponentSelection  # type: ignore
    except Exception:  # noqa: BLE001
        from app.marcus.orchestrator.production_runner import ComponentSelection  # type: ignore

    manifest = compose_manifest(
        load_manifest(REPO / "state/config/pipeline-manifest.yaml"),
        ComponentSelection.production_default(),
    )
    for i, node in enumerate(manifest.nodes):
        if node.id == node_id:
            return i, getattr(node, "specialist_id", None)
    raise SystemExit(f"node {node_id!r} not present in the composed manifest")


# ---------------------------------------------------------------------------
# prepare: copy golden -> new dir, rewire ids, reposition recover point, mint RAI
# ---------------------------------------------------------------------------


def prepare(new_trial: UUID) -> dict[str, object]:
    new_id = str(new_trial)
    new_dir = RUNS_ROOT_ABS / new_id
    if new_dir.exists():
        raise SystemExit(f"refusing to overwrite existing run dir {new_dir}")
    if not GOLDEN_DIR.is_dir():
        raise SystemExit(f"golden dir missing: {GOLDEN_DIR}")

    log(f"copy {GOLDEN_DIR}  ->  {new_dir}")
    shutil.copytree(GOLDEN_DIR, new_dir)

    consumer_idx, consumer_sid = _composed_node_index(CONSUMER_NODE_ID)
    if consumer_sid != CONSUMER_SPECIALIST_ID:
        raise SystemExit(
            f"composed manifest node {CONSUMER_NODE_ID!r} specialist "
            f"{consumer_sid!r} != expected {CONSUMER_SPECIALIST_ID!r}"
        )

    # ---- run.json: surgical id rewrite ONLY (no contribution edits) ----
    run_path = new_dir / "run.json"
    run = json.loads(run_path.read_text(encoding="utf-8"))
    run["trial_id"] = new_id
    if run.get("langsmith_trace_id") == GOLDEN_TRIAL:
        run["langsmith_trace_id"] = new_id
    if isinstance(run.get("cost_report_path"), str):
        run["cost_report_path"] = run["cost_report_path"].replace(GOLDEN_TRIAL, new_id)
    if isinstance(run.get("artifact_paths"), list):
        run["artifact_paths"] = [
            p.replace(GOLDEN_TRIAL, new_id) if isinstance(p, str) else p
            for p in run["artifact_paths"]
        ]
    run["production_envelope"]["trial_id"] = new_id  # not digest-protected
    # DROP the consumer's existing contribution so first-wins re-dispatches it. Every
    # OTHER contribution is left byte-identical (output_digests intact).
    contribs = run["production_envelope"]["contributions"]
    dropped = [
        c for c in contribs
        if c.get("specialist_id") == CONSUMER_SPECIALIST_ID and c.get("node_id") == CONSUMER_NODE_ID
    ]
    run["production_envelope"]["contributions"] = [
        c for c in contribs
        if not (c.get("specialist_id") == CONSUMER_SPECIALIST_ID and c.get("node_id") == CONSUMER_NODE_ID)
    ]
    run_path.write_text(json.dumps(run, indent=2, default=str), encoding="utf-8")
    log(
        f"run.json rewritten: trial_id={new_id}; dropped "
        f"{len(dropped)} {CONSUMER_SPECIALIST_ID}@{CONSUMER_NODE_ID} contribution(s) "
        f"(remaining={len(run['production_envelope']['contributions'])})"
    )
    if not dropped:
        raise SystemExit(
            f"expected an existing {CONSUMER_SPECIALIST_ID}@{CONSUMER_NODE_ID} "
            "contribution to drop, found none"
        )

    # ---- error-pause.json: id rewrite + REPOSITION recover point to gary@07 ----
    ep_path = new_dir / "error-pause.json"
    ep = json.loads(ep_path.read_text(encoding="utf-8"))
    ep["trial_id"] = new_id
    ep["node_index"] = consumer_idx
    ep["node_id"] = CONSUMER_NODE_ID
    ep["specialist_id"] = CONSUMER_SPECIALIST_ID
    ep["tag"] = f"leg4.udac-proof.repositioned-to-{CONSUMER_SPECIALIST_ID}-consumer"
    ep["message"] = (
        f"recover point repositioned to the g0-enrichment consumer "
        f"{CONSUMER_SPECIALIST_ID} (node {CONSUMER_NODE_ID}) for the UDAC "
        "anti-tautology broken-asset HALT proof"
    )
    rs = ep["run_state"]
    rs["run_id"] = new_id
    if isinstance(rs.get("production_envelope"), dict):
        rs["production_envelope"]["trial_id"] = new_id
        # recover replaces run_state.production_envelope with the run.json envelope,
        # but drop here too for consistency.
        rspe = rs["production_envelope"]
        if isinstance(rspe.get("contributions"), list):
            rspe["contributions"] = [
                c for c in rspe["contributions"]
                if not (
                    c.get("specialist_id") == CONSUMER_SPECIALIST_ID
                    and c.get("node_id") == CONSUMER_NODE_ID
                )
            ]
    runner = ep.get("runner") or {}
    for pk in ("directive_path", "bundle_dir"):
        if isinstance(runner.get(pk), str):
            runner[pk] = runner[pk].replace(GOLDEN_TRIAL, new_id)
    ep_path.write_text(json.dumps(ep, indent=2, default=str), encoding="utf-8")
    log(
        f"error-pause.json repositioned: node_index={consumer_idx} "
        f"node_id={CONSUMER_NODE_ID} specialist_id={CONSUMER_SPECIALIST_ID} "
        f"last_gate_crossed={ep.get('last_gate_crossed')}"
    )

    # ---- directive.yaml: keep run_id internally consistent (no digest) ----
    dpath = new_dir / "directive.yaml"
    if dpath.is_file():
        txt = dpath.read_text(encoding="utf-8")
        if GOLDEN_TRIAL in txt:
            dpath.write_text(txt.replace(GOLDEN_TRIAL, new_id), encoding="utf-8")
            log("directive.yaml run_id retargeted to new trial")

    # ---- MINT the RAI on the CLEAN g0-enrichment.json (real disk digest) ----
    os.environ["MARCUS_UDAC_ACTIVE"] = "1"
    from app.marcus.lesson_plan.run_asset_index import (  # type: ignore
        DigestAlgo,
        recompute_digest_from_disk,
    )
    from app.marcus.orchestrator.udac_wiring import record_gate_ratification  # type: ignore

    clean_digest = recompute_digest_from_disk(
        new_dir / ASSET_REL_PATH, DigestAlgo.CANONICAL_SHA256
    )
    index = record_gate_ratification(gate_code=RATIFYING_GATE, run_dir=new_dir)
    if index is None:
        raise SystemExit("record_gate_ratification returned None — RAI not minted")
    entry = index.get(ASSET_ID)
    if entry is None:
        raise SystemExit(f"RAI has no {ASSET_ID!r} entry after mint")
    rai_file = new_dir / "run-asset-index.json"
    log(
        f"RAI minted: {rai_file.name} pins {ASSET_ID} status={entry.authority_status} "
        f"digest={str(entry.digest)[:12]}… (disk={clean_digest[:12]}…) "
        f"produced_by={entry.produced_by_node}"
    )
    if entry.digest != clean_digest:
        raise SystemExit("RAI digest != freshly recomputed disk digest")

    return {
        "new_trial": new_id,
        "new_dir": str(new_dir),
        "consumer_node_index": consumer_idx,
        "consumer_node_id": CONSUMER_NODE_ID,
        "consumer_specialist_id": CONSUMER_SPECIALIST_ID,
        "rai_path": str(rai_file),
        "rai_ratified_digest": entry.digest,
        "clean_disk_digest": clean_digest,
        "asset_authority_status": str(entry.authority_status),
        "asset_produced_by": entry.produced_by_node,
        "directive_path": runner.get("directive_path"),
        "bundle_dir": runner.get("bundle_dir"),
        "last_gate_crossed": ep.get("last_gate_crossed"),
    }


# ---------------------------------------------------------------------------
# corruption (DIGEST-mutating, still valid JSON -> TAG_STALE, not TAG_CORRUPT)
# ---------------------------------------------------------------------------


def _corrupt_asset(new_dir: Path) -> dict[str, object]:
    """Mutate g0-enrichment.json CONTENT (add a benign key) so it stays valid JSON
    but its canonical_sha256 diverges -> a STALE digest mismatch, NOT a parse
    failure. Returns before/after digests."""
    from app.marcus.lesson_plan.run_asset_index import (  # type: ignore
        DigestAlgo,
        recompute_digest_from_disk,
    )

    apath = new_dir / ASSET_REL_PATH
    before = recompute_digest_from_disk(apath, DigestAlgo.CANONICAL_SHA256)
    payload = json.loads(apath.read_text(encoding="utf-8"))
    payload["_leg4_udac_corruption_marker"] = f"mutated-{int(time.time())}"
    apath.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    # still valid JSON:
    json.loads(apath.read_text(encoding="utf-8"))
    after = recompute_digest_from_disk(apath, DigestAlgo.CANONICAL_SHA256)
    assert before != after, "corruption did not change the digest"
    return {"digest_before": before, "digest_after": after, "still_valid_json": True}


# ---------------------------------------------------------------------------
# offline plumbing validation (no runner, no live API)
# ---------------------------------------------------------------------------


def offline_validate(new_trial: UUID) -> dict[str, object]:
    """Validate the prepared plumbing WITHOUT invoking the live recover.

    Exercises the EXACT reader path (resolve_consumed_assets -> resolve_asset ->
    recompute_digest_from_disk): PASS on the clean file, RAISE tag=udac.asset-stale
    on a temp-corrupted-then-restored file.
    """
    os.environ["MARCUS_UDAC_ACTIVE"] = "1"
    from app.marcus.lesson_plan.run_asset_index import (  # type: ignore
        CONSUMER_REGISTRY,
        TAG_STALE,
        AssetResolutionError,
    )
    from app.marcus.orchestrator.udac_wiring import (  # type: ignore
        resolve_consumed_assets,
        udac_active,
    )
    from app.models.runtime.production_trial_envelope import (  # type: ignore
        ProductionTrialEnvelope,
    )

    new_dir = RUNS_ROOT_ABS / str(new_trial)
    checks: dict[str, object] = {}
    checks["udac_active"] = udac_active()

    # (a) the copied run.json loads (all contribution digests still valid).
    env = ProductionTrialEnvelope.model_validate_json(
        (new_dir / "run.json").read_text(encoding="utf-8"),
        context={"anomaly_sink": new_dir / "anomalies.jsonl"},
    )
    checks["run_json_loads"] = True
    checks["envelope_status"] = env.status
    checks["envelope_trial_id_matches"] = str(env.trial_id) == str(new_trial)
    # consumer contribution DROPPED so first-wins will re-dispatch it.
    checks["consumer_contribution_dropped"] = not any(
        c.specialist_id == CONSUMER_SPECIALIST_ID and c.node_id == CONSUMER_NODE_ID
        for c in env.production_envelope.contributions
    )

    # (b) registry: the chosen consumer (gary) declares g0-enrichment as USED.
    decl = CONSUMER_REGISTRY.get(CONSUMER_SPECIALIST_ID)
    checks["consumer_registered"] = decl is not None
    checks["consumer_uses_asset"] = bool(decl and ASSET_ID in decl.required_assets())

    # (c) CLEAN resolve PASSES (control path wired).
    resolved = resolve_consumed_assets(
        specialist_id=CONSUMER_SPECIALIST_ID, run_dir=new_dir
    )
    checks["clean_resolve_returns"] = resolved is not None and ASSET_ID in (resolved or {})

    # (d) CORRUPT resolve RAISES tag=udac.asset-stale (halt path wired) — temp,
    #     then RESTORE the clean bytes so the dir is left ready for a --live recover.
    apath = new_dir / ASSET_REL_PATH
    clean_bytes = apath.read_bytes()
    stale_raised = False
    stale_tag = None
    try:
        _corrupt_asset(new_dir)
        try:
            resolve_consumed_assets(
                specialist_id=CONSUMER_SPECIALIST_ID, run_dir=new_dir
            )
        except AssetResolutionError as exc:
            stale_raised = True
            stale_tag = getattr(exc, "tag", None)
    finally:
        apath.write_bytes(clean_bytes)  # restore clean
    checks["corrupt_resolve_raises"] = stale_raised
    checks["corrupt_tag"] = stale_tag
    checks["corrupt_tag_is_stale"] = stale_tag == TAG_STALE
    checks["asset_restored_clean"] = apath.read_bytes() == clean_bytes

    # (e) recover-point sanity: node_index maps to gary@07 in composed manifest.
    ci, csid = _composed_node_index(CONSUMER_NODE_ID)
    ep = json.loads((new_dir / "error-pause.json").read_text(encoding="utf-8"))
    checks["recover_point"] = {
        "node_index": ep["node_index"],
        "node_id": ep["node_id"],
        "specialist_id": ep["specialist_id"],
        "composed_index_matches": ep["node_index"] == ci,
        "composed_specialist_matches": csid == CONSUMER_SPECIALIST_ID,
        "last_gate_crossed": ep.get("last_gate_crossed"),
    }
    checks["ALL_OFFLINE_CHECKS_PASS"] = bool(
        checks["run_json_loads"]
        and checks["envelope_trial_id_matches"]
        and checks["consumer_contribution_dropped"]
        and checks["consumer_registered"]
        and checks["consumer_uses_asset"]
        and checks["clean_resolve_returns"]
        and checks["corrupt_resolve_raises"]
        and checks["corrupt_tag_is_stale"]
        and checks["asset_restored_clean"]
        and checks["recover_point"]["composed_index_matches"]
        and checks["recover_point"]["composed_specialist_matches"]
    )
    return checks


# ---------------------------------------------------------------------------
# audio / spend accounting ($0 assertion helpers)
# ---------------------------------------------------------------------------


def _audio_spend_snapshot(new_dir: Path) -> dict[str, object]:
    mp3 = [str(p) for p in new_dir.rglob("*.mp3")]
    wav = [str(p) for p in new_dir.rglob("*.wav")]
    return {"mp3_count": len(mp3), "wav_count": len(wav), "mp3": mp3, "wav": wav}


# ---------------------------------------------------------------------------
# live recover arms
# ---------------------------------------------------------------------------


def live_halt(new_trial: UUID) -> dict[str, object]:
    """--halt --live: corrupt g0-enrichment.json, recover, assert udac.asset-stale
    halt at gary@07 with $0 spend."""
    from app.marcus.orchestrator.production_runner import (  # type: ignore
        recover_production_trial,
    )

    os.environ["MARCUS_UDAC_ACTIVE"] = "1"
    new_dir = RUNS_ROOT_ABS / str(new_trial)
    corruption = _corrupt_asset(new_dir)
    log(f"CORRUPTED {ASSET_REL_PATH}: {corruption['digest_before'][:12]}… -> "
        f"{corruption['digest_after'][:12]}… (valid JSON, digest mismatch)")

    audio_before = _audio_spend_snapshot(new_dir)
    log("LIVE recover_production_trial(max_specialist_calls=1) — expect a UDAC halt "
        "BEFORE any gpt call…")
    env = recover_production_trial(
        trial_id=new_trial, runs_root=RUNS_ROOT_ABS, max_specialist_calls=1
    )
    audio_after = _audio_spend_snapshot(new_dir)

    ep = json.loads((new_dir / "error-pause.json").read_text(encoding="utf-8"))
    # The guard must fire BEFORE the consumer produces anything: gary@07 stays ABSENT
    # in the paused envelope (its paid Gamma call never ran).
    consumer_present = any(
        c.specialist_id == CONSUMER_SPECIALIST_ID and c.node_id == CONSUMER_NODE_ID
        for c in env.production_envelope.contributions
    )
    result: dict[str, object] = {
        "corruption": corruption,
        "walk_status": env.status,
        "error_pause_tag": ep.get("tag"),
        "error_pause_node_id": ep.get("node_id"),
        "error_pause_specialist_id": ep.get("specialist_id"),
        "error_pause_message": ep.get("message"),
        "consumer_contribution_present": consumer_present,
        "audio_before": audio_before,
        "audio_after": audio_after,
    }
    result["status_is_paused_at_error"] = env.status == "paused-at-error"
    result["tag_is_udac_stale"] = ep.get("tag") == "udac.asset-stale"
    result["halt_at_consumer"] = (
        ep.get("node_id") == CONSUMER_NODE_ID
        and ep.get("specialist_id") == CONSUMER_SPECIALIST_ID
    )
    result["paid_call_prevented"] = not consumer_present  # gary Gamma call never fired
    result["zero_mp3"] = audio_after["mp3_count"] == 0
    result["zero_wav"] = audio_after["wav_count"] == 0
    result["no_new_audio"] = (
        audio_after["mp3_count"] == audio_before["mp3_count"]
        and audio_after["wav_count"] == audio_before["wav_count"]
    )
    result["HALT_PROVEN"] = bool(
        result["status_is_paused_at_error"]
        and result["tag_is_udac_stale"]
        and result["halt_at_consumer"]
        and result["paid_call_prevented"]
        and result["zero_mp3"]
        and result["zero_wav"]
    )
    log(f"  -> status={env.status} tag={ep.get('tag')} node={ep.get('node_id')} "
        f"specialist={ep.get('specialist_id')} HALT_PROVEN={result['HALT_PROVEN']}")
    return result


def live_control(new_trial: UUID) -> dict[str, object]:
    """--control --live: recover WITHOUT corruption; assert the guard did NOT halt
    (sails past to the next dispatch/gate)."""
    from app.marcus.orchestrator.production_runner import (  # type: ignore
        recover_production_trial,
    )

    os.environ["MARCUS_UDAC_ACTIVE"] = "1"
    new_dir = RUNS_ROOT_ABS / str(new_trial)
    log("LIVE recover_production_trial(max_specialist_calls=1) — CLEAN asset, expect "
        "the guard to PASS and gary to re-dispatch (paid Gamma) / walk to advance…")
    env = recover_production_trial(
        trial_id=new_trial, runs_root=RUNS_ROOT_ABS, max_specialist_calls=1
    )
    ep_path = new_dir / "error-pause.json"
    # If the walk paused at a GATE (not an error) the error-pause.json is the STALE
    # pre-recover file; distinguish by env.status.
    ep = json.loads(ep_path.read_text(encoding="utf-8")) if ep_path.is_file() else {}

    # first-wins: a gary@07 contribution now present means gary actually re-dispatched.
    consumer_present = any(
        c.specialist_id == CONSUMER_SPECIALIST_ID and c.node_id == CONSUMER_NODE_ID
        for c in env.production_envelope.contributions
    )

    result: dict[str, object] = {
        "walk_status": env.status,
        "paused_gate": getattr(env, "paused_gate", None),
        "paused_error_tag": getattr(env, "paused_error_tag", None),
        "error_pause_tag_on_disk": ep.get("tag"),
        "error_pause_node_on_disk": ep.get("node_id"),
        "consumer_contribution_present": consumer_present,
    }
    # The discriminator: the CLEAN recover must NOT be a udac.asset-stale halt at the
    # consumer node. (A gate pause, completion, or the consumer re-dispatching all
    # satisfy "sailed past the guard".)
    is_udac_stale_halt = (
        env.status == "paused-at-error"
        and getattr(env, "paused_error_tag", None) == "udac.asset-stale"
    )
    result["is_udac_stale_halt"] = is_udac_stale_halt
    result["sailed_past_guard"] = not is_udac_stale_halt
    # Strong form: gary re-dispatched its paid Gamma call (proves the "next paid
    # dispatch" actually fires when the asset is clean).
    result["consumer_redispatched"] = consumer_present
    result["CONTROL_PROVEN"] = not is_udac_stale_halt
    log(f"  -> status={env.status} paused_error_tag={getattr(env,'paused_error_tag',None)} "
        f"paused_gate={getattr(env,'paused_gate',None)} "
        f"{CONSUMER_SPECIALIST_ID}{CONSUMER_NODE_ID}_present={consumer_present} "
        f"CONTROL_PROVEN={result['CONTROL_PROVEN']}")
    return result


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--trial-id", default=None)
    ap.add_argument("--live", action="store_true", help="run the live recover walk")
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--build", action="store_true", help="offline prepare + validate")
    mode.add_argument("--halt", action="store_true", help="the STALE/HALT arm")
    mode.add_argument("--control", action="store_true", help="the CLEAN/CONTROL arm")
    mode.add_argument("--all", action="store_true", help="offline both arms (+live if --live)")
    args = ap.parse_args()

    which = "build" if args.build else "halt" if args.halt else "control" if args.control else "all"
    log(f"MODE={which}  LIVE={args.live}")

    env_report = _load_env_override(require_live=bool(args.live))
    log("env load:", env_report, "OPENAI_API_KEY:", _mask(os.environ.get("OPENAI_API_KEY")))

    out: dict[str, object] = {"mode": which, "live": bool(args.live)}
    try:
        if which in ("build",) or (which == "all" and not args.live):
            # offline: prepare one (or two) trials + validate, no live recover.
            arms = ["build"] if which == "build" else ["halt-arm", "control-arm"]
            out["arms"] = {}
            for arm in arms:
                t = UUID(args.trial_id) if (args.trial_id and len(arms) == 1) else uuid4()
                prep = prepare(t)
                checks = offline_validate(t)
                out["arms"][arm] = {"prepare": prep, "offline_checks": checks}
            passed = all(
                a["offline_checks"]["ALL_OFFLINE_CHECKS_PASS"] for a in out["arms"].values()
            )
            out["VERDICT"] = "OFFLINE-OK" if passed else "OFFLINE-FAILED"

        elif which == "halt":
            t = UUID(args.trial_id) if args.trial_id else uuid4()
            out["prepare"] = prepare(t)
            if args.live:
                out["live_halt"] = live_halt(t)
                out["VERDICT"] = "LIVE-HALT-OK" if out["live_halt"]["HALT_PROVEN"] else "LIVE-HALT-FAILED"
            else:
                out["offline_checks"] = offline_validate(t)
                out["VERDICT"] = (
                    "OFFLINE-OK" if out["offline_checks"]["ALL_OFFLINE_CHECKS_PASS"] else "OFFLINE-FAILED"
                )

        elif which == "control":
            t = UUID(args.trial_id) if args.trial_id else uuid4()
            out["prepare"] = prepare(t)
            if args.live:
                out["live_control"] = live_control(t)
                out["VERDICT"] = "LIVE-CONTROL-OK" if out["live_control"]["CONTROL_PROVEN"] else "LIVE-CONTROL-FAILED"
            else:
                out["offline_checks"] = offline_validate(t)
                out["VERDICT"] = (
                    "OFFLINE-OK" if out["offline_checks"]["ALL_OFFLINE_CHECKS_PASS"] else "OFFLINE-FAILED"
                )

        elif which == "all" and args.live:
            th = uuid4()
            out["halt_prepare"] = prepare(th)
            out["live_halt"] = live_halt(th)
            tc = uuid4()
            out["control_prepare"] = prepare(tc)
            out["live_control"] = live_control(tc)
            out["VERDICT"] = (
                "LIVE-ALL-OK"
                if out["live_halt"]["HALT_PROVEN"] and out["live_control"]["CONTROL_PROVEN"]
                else "LIVE-ALL-FAILED"
            )
    except Exception as exc:  # noqa: BLE001
        out["exception"] = f"{type(exc).__name__}: {exc}"
        out["traceback"] = traceback.format_exc()
        out["VERDICT"] = "ERROR"

    print("\n===== RESULT =====")
    print(json.dumps(out, indent=2, default=str))
    return 0 if str(out.get("VERDICT", "")).endswith("OK") else 1


if __name__ == "__main__":
    raise SystemExit(main())
