"""Leg-2 motion-isolation REPROVE driver — REWIND-RECOVER a live Kling render
through the production_runner CONTINUATION walk.

WHAT THIS PROVES
----------------
The Leg-2 isolation fix (``_runner_payload_for_specialist`` threads
``bundle_path = runs_root/<trial_id>`` UNCONDITIONALLY for kira, with NO seed
env) routes kira's motion receipts + downloaded .mp4 to the PER-RUN dir
``state/config/runs/<trial_id>/motion/`` on a *recover*. Proving a run-scoped
mp4 lands there IS the acceptance proof.

MECHANISM (rewind-recover of a COPY; golden 8d819b8d is NEVER touched)
    1. Copy golden run dir -> state/config/runs/<NEW_TRIAL>/.
    2. SURGICALLY rewrite trial-id fields in run.json + error-pause.json to
       <NEW_TRIAL> (NOT a global text replace: several contribution OUTPUTS
       embed the golden UUID in absolute paths, and each contribution's
       output_digest is HARD-VALIDATED on load -- a blanket replace would
       break those digests. So we touch only the non-digest-protected id
       fields + the runner directive/bundle paths, and leave every
       contribution.output -- and thus every output_digest -- byte-identical).
    3. Make it motion-worthy: the golden's stored 07D.5 motion_plan is EMPTY
       (slides:[]  -> paused-at-error tag kira.motion-plan.empty). We edit the
       persisted motion_planner@07D.5 contribution's output.motion_plan to a
       single B2 text2video slide (kling-v1-6 / std / 5s / 16:9 / NO image_url
       / sound OMITTED) and RECOMPUTE that one contribution's output_digest.
       Node 07E (kira) has dependency_projections {motion_plan: from
       motion_planner, key motion_plan}, so the dispatch adapter projects this
       exact dict into kira's payload -> kira._load_motion_plan returns it ->
       text_to_video fires (paid Kling call), NOT a floor still.
    4. --live: recover_production_trial(trial_id=<NEW>, runs_root=..,
       max_specialist_calls=1) re-enters UNSHIFTED at node_index=30 (07E).
       kira has no contribution -> first-wins re-dispatches ONLY kira, then the
       walk pauses at the next gate (G2F/G3). Assert a run-scoped mp4 + success
       receipt. --dry-run does everything EXCEPT the recover call and instead
       validates the prepared plumbing offline (no live keys required).

USAGE
    python scratchpad/leg2_motion_reprove_driver.py --dry-run [--trial-id UUID]
    python scratchpad/leg2_motion_reprove_driver.py --live    [--trial-id UUID]
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

# B2 proven text2video prompt (source: runs/kira-motion-b2/v1-6/motion/b2-kling-v1-6.progress.json)
B2_PROMPT = (
    "Smooth cinematic push-in on a clean abstract teal-and-white "
    "medical-education title background: soft glowing molecular lattice, "
    "gentle particle drift, calm authoritative tone. Subtle, professional "
    "motion suitable for a lesson intro."
)


def log(*a: object) -> None:
    print(f"[{time.strftime('%H:%M:%S')}]", *a, flush=True)


def _b2_slide() -> dict[str, object]:
    """The single motion-worthy slide injected into the 07D.5 motion_plan.

    NO image_url / visual_file -> kira takes the text_to_video path.
    sound OMITTED (absent) -> Kling body omits `sound` (avoids code=1201).
    estimated_cost_usd within kira per-invocation cap (0.40) and daily (5.00).
    """
    return {
        "slide_id": "b2-title-motion",
        "kling_prompt": B2_PROMPT,
        "model_name": "kling-v1-6",
        "mode": "std",
        "duration": "5",
        "aspect_ratio": "16:9",
        "estimated_cost_usd": 0.28,
    }


def _load_env_override(require_live: bool) -> dict[str, str]:
    """Mirror the coverage driver's .env load with override (handles the
    sk-subst sentinel gotcha: repo env_loader only sets if-absent, so a stale
    sentinel in os.environ would shadow the real key)."""
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
        assert key.startswith("sk-"), "live OPENAI_API_KEY not loaded (starts with sk-)"
    return report


def _mask(val: str | None) -> str:
    if not val:
        return "ABSENT"
    v = val.strip()
    if len(v) <= 10:
        return f"present(len={len(v)}, …masked…)"
    return f"present(len={len(v)}, {v[:6]}…{v[-4:]})"


def _read_dotenv_keys() -> dict[str, str]:
    """Read .env DIRECTLY (do not print secret values) and report presence."""
    env_path = REPO / ".env"
    kv: dict[str, str] = {}
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            kv[k.strip()] = v.strip()
    wanted = ["OPENAI_API_KEY", "KLING_ACCESS_KEY", "KLING_SECRET_KEY", "KLING_API_TOKEN"]
    out = {k: _mask(kv.get(k)) for k in wanted}
    has_openai = bool(kv.get("OPENAI_API_KEY"))
    has_kling = bool(kv.get("KLING_API_TOKEN")) or (
        bool(kv.get("KLING_ACCESS_KEY")) and bool(kv.get("KLING_SECRET_KEY"))
    )
    out["_verdict"] = (
        "OK (openai + kling present)"
        if (has_openai and has_kling)
        else f"INCOMPLETE (openai={has_openai}, kling={has_kling})"
    )
    return out


def prepare(new_trial: UUID) -> dict[str, object]:
    """Copy golden -> new run dir; surgically rewrite ids; inject B2 motion plan."""
    from app.models.runtime.production_envelope import compute_output_digest

    new_id = str(new_trial)
    new_dir = RUNS_ROOT_ABS / new_id
    if new_dir.exists():
        raise SystemExit(f"refusing to overwrite existing run dir {new_dir}")
    if not GOLDEN_DIR.is_dir():
        raise SystemExit(f"golden dir missing: {GOLDEN_DIR}")

    log(f"copy {GOLDEN_DIR}  ->  {new_dir}")
    shutil.copytree(GOLDEN_DIR, new_dir)

    # ---- run.json: surgical id rewrite + motion-worthy injection ----
    run_path = new_dir / "run.json"
    run = json.loads(run_path.read_text(encoding="utf-8"))
    run["trial_id"] = new_id
    if run.get("langsmith_trace_id") == GOLDEN_TRIAL:
        run["langsmith_trace_id"] = new_id
    # cosmetic path fields (NOT digest-protected) -> point at the new run dir
    if isinstance(run.get("cost_report_path"), str):
        run["cost_report_path"] = run["cost_report_path"].replace(GOLDEN_TRIAL, new_id)
    if isinstance(run.get("artifact_paths"), list):
        run["artifact_paths"] = [
            p.replace(GOLDEN_TRIAL, new_id) if isinstance(p, str) else p
            for p in run["artifact_paths"]
        ]
    pe = run["production_envelope"]
    pe["trial_id"] = new_id  # envelope.trial_id is NOT digest-protected

    mp = next(c for c in pe["contributions"] if c["specialist_id"] == "motion_planner")
    old_digest = mp["output_digest"]
    new_output = {
        "motion_plan": {"slides": [_b2_slide()]},
        "motion_planner": {"slide_count": 1, "specialist_id": "motion_planner"},
    }
    mp["output"] = new_output
    mp["output_digest"] = compute_output_digest(new_output)  # RECOMPUTE (hard-validated)
    run_path.write_text(json.dumps(run, indent=2, default=str), encoding="utf-8")
    log(f"run.json rewritten: trial_id={new_id}; motion_planner digest "
        f"{old_digest[:12]}… -> {mp['output_digest'][:12]}…")

    # ---- error-pause.json: surgical id rewrite + runner path retarget ----
    ep_path = new_dir / "error-pause.json"
    ep = json.loads(ep_path.read_text(encoding="utf-8"))
    ep["trial_id"] = new_id
    rs = ep["run_state"]
    rs["run_id"] = new_id
    if isinstance(rs.get("production_envelope"), dict):
        rs["production_envelope"]["trial_id"] = new_id
    runner = ep.get("runner") or {}
    for pk in ("directive_path", "bundle_dir"):
        if isinstance(runner.get(pk), str):
            runner[pk] = runner[pk].replace(GOLDEN_TRIAL, new_id)
    # keep node_index=30 / node_id=07E / last_gate_crossed unchanged (re-enter at kira)
    ep_path.write_text(json.dumps(ep, indent=2, default=str), encoding="utf-8")
    log(f"error-pause.json rewritten: node_index={ep['node_index']} "
        f"node_id={ep['node_id']} last_gate_crossed={ep.get('last_gate_crossed')}")

    # ---- directive.yaml: keep run_id internally consistent (no digest) ----
    dpath = new_dir / "directive.yaml"
    if dpath.is_file():
        txt = dpath.read_text(encoding="utf-8")
        if GOLDEN_TRIAL in txt:
            dpath.write_text(txt.replace(GOLDEN_TRIAL, new_id), encoding="utf-8")
            log("directive.yaml run_id retargeted to new trial")

    return {
        "new_trial": new_id,
        "new_dir": str(new_dir),
        "motion_dir": str(new_dir / "motion"),
        "directive_path": runner.get("directive_path"),
        "bundle_dir": runner.get("bundle_dir"),
    }


def dry_run_checks(new_trial: UUID, prep: dict[str, object]) -> dict[str, object]:
    """Offline plumbing validation (no live keys, no dispatch)."""
    from app.models.runtime.production_trial_envelope import ProductionTrialEnvelope
    from app.models.state.run_state import RunState
    from app.specialists.kira._act import (
        _load_motion_plan,
        _prompt_for,
        _slides_from_plan,
    )

    new_dir = RUNS_ROOT_ABS / str(new_trial)
    checks: dict[str, object] = {}

    # (a) copied run.json loads (all digests valid incl recomputed motion_planner)
    env = ProductionTrialEnvelope.model_validate_json(
        (new_dir / "run.json").read_text(encoding="utf-8"),
        context={"anomaly_sink": new_dir / "anomalies.jsonl"},
    )
    checks["run_json_loads"] = True
    checks["envelope_status"] = env.status
    checks["envelope_trial_id"] = str(env.trial_id)
    checks["envelope_trial_id_matches"] = str(env.trial_id) == str(new_trial)

    # (b) injected plan is motion-worthy (won't trip the floor / won't starve kira)
    mp = next(
        c for c in env.production_envelope.contributions
        if c.specialist_id == "motion_planner"
    )
    payload = {"motion_plan": mp.output["motion_plan"]}
    plan = _load_motion_plan(payload)
    slides = _slides_from_plan(plan)
    first = slides[0] if slides else {}
    checks["motion_worthy"] = {
        "n_slides": len(slides),
        "slide_id": first.get("slide_id"),
        "prompt_is_b2": _prompt_for(first) == B2_PROMPT,
        "has_image_url": bool(first.get("image_url") or first.get("visual_file")),
        "model_name": first.get("model_name"),
        "mode": first.get("mode"),
        "duration": first.get("duration"),
        "aspect_ratio": first.get("aspect_ratio"),
        "estimated_cost_usd": first.get("estimated_cost_usd"),
    }
    assert len(slides) == 1, "expected exactly one injected slide"
    assert _prompt_for(first) == B2_PROMPT, "injected prompt is not the B2 prompt"
    assert not (first.get("image_url") or first.get("visual_file")), (
        "slide has image_url -> would take image2video, not the paid text2video path"
    )

    # (c) error-pause.json well-formed + RunState re-hydrates
    ep = json.loads((new_dir / "error-pause.json").read_text(encoding="utf-8"))
    rs = RunState.model_validate_json(json.dumps(ep["run_state"]))
    checks["error_pause"] = {
        "trial_id": ep["trial_id"],
        "trial_id_matches": ep["trial_id"] == str(new_trial),
        "node_index": ep["node_index"],
        "node_id": ep["node_id"],
        "last_gate_crossed": ep.get("last_gate_crossed"),
        "run_state_run_id": str(rs.run_id),
        "run_state_run_id_matches": str(rs.run_id) == str(new_trial),
        "runner_directive_in_new_dir": str(new_trial) in str(ep["runner"]["directive_path"]),
        "runner_bundle_in_new_dir": str(new_trial) in str(ep["runner"]["bundle_dir"]),
    }
    assert ep["node_index"] == 30 and ep["node_id"] == "07E", "re-entry node drifted"

    # (d) target motion dir is run-scoped under state/config/runs/<NEW_TRIAL>
    expected_motion = RUNS_ROOT_ABS / str(new_trial) / "motion"
    checks["target_motion_dir"] = str(expected_motion)
    checks["target_motion_dir_run_scoped"] = (
        expected_motion.parent.name == str(new_trial)
        and expected_motion.parent.parent == RUNS_ROOT_ABS
    )
    return checks


def isolation_fix_check(new_trial: UUID) -> dict[str, object]:
    """Step 3: call _runner_payload_for_specialist directly, offline, no dispatch."""
    os.environ.pop("KIRA_MOTION_PLAN_PATH", None)  # ensure seed env unset
    from app.marcus.orchestrator.production_runner import _runner_payload_for_specialist

    payload = _runner_payload_for_specialist(
        specialist_id="kira",
        directive_path=RUNS_ROOT_REL / str(new_trial) / "directive.yaml",
        bundle_dir=RUNS_ROOT_REL / str(new_trial) / "bundle",
        gate_code=None,
        production_envelope=None,
        runs_root=RUNS_ROOT_REL,
        trial_id=new_trial,
    )
    expected_bundle = (RUNS_ROOT_REL / str(new_trial)).as_posix()
    return {
        "payload": payload,
        "bundle_path": (payload or {}).get("bundle_path"),
        "bundle_path_matches": (payload or {}).get("bundle_path") == expected_bundle,
        "no_motion_plan_path": "motion_plan_path" not in (payload or {}),
    }


def live_recover(new_trial: UUID) -> dict[str, object]:
    """--live only: run the continuation walk and assert a run-scoped mp4."""
    from app.marcus.orchestrator.production_runner import recover_production_trial

    os.environ.pop("KIRA_MOTION_PLAN_PATH", None)  # NO seed env — prove unconditional bundle_path
    new_dir = RUNS_ROOT_ABS / str(new_trial)
    log("LIVE recover_production_trial(max_specialist_calls=1) — single paid Kling render…")
    env = recover_production_trial(
        trial_id=new_trial,
        runs_root=RUNS_ROOT_ABS,
        max_specialist_calls=1,
    )
    log(f"  -> status={env.status} paused_gate={env.paused_gate}")

    motion_dir = new_dir / "motion"
    mp4s = sorted(motion_dir.glob("*.mp4")) if motion_dir.is_dir() else []
    result: dict[str, object] = {
        "walk_status": env.status,
        "paused_gate": env.paused_gate,
        "motion_dir": str(motion_dir),
        "mp4_files": [str(p) for p in mp4s],
    }
    assert mp4s, f"NO mp4 under run-scoped {motion_dir} — isolation/render failed"
    mp4 = mp4s[0]
    head = mp4.read_bytes()[:64]
    result["mp4_bytes"] = mp4.stat().st_size
    result["has_ftyp"] = b"ftyp" in head
    result["has_moov_or_mdat"] = (b"moov" in mp4.read_bytes()[:4096]) or (b"mdat" in mp4.read_bytes()[:8192])
    assert result["has_ftyp"], "mp4 missing ftyp box"

    receipt_path = motion_dir / f"{mp4.stem}.json"
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    result["receipt_status"] = receipt.get("status")
    ct = receipt.get("cost_tracking") or {}
    result["actual_cost_usd"] = ct.get("actual_cost_usd")
    assert receipt.get("status") == "success", f"receipt status={receipt.get('status')}"
    assert float(ct.get("actual_cost_usd") or 0) > 0, "zero cost deduction — not a paid render"

    run = json.loads((new_dir / "run.json").read_text(encoding="utf-8"))
    result["run_json_references_motion"] = str(mp4) in json.dumps(run) or "motion" in json.dumps(run)
    return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--trial-id", default=None)
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--live", action="store_true")
    args = ap.parse_args()

    sys.path.insert(0, str(REPO))
    new_trial = UUID(args.trial_id) if args.trial_id else uuid4()
    log(f"MODE={'live' if args.live else 'dry-run'}  NEW_TRIAL={new_trial}")

    env_report = _load_env_override(require_live=bool(args.live))
    log("env load:", env_report)

    out: dict[str, object] = {"new_trial": str(new_trial), "mode": "live" if args.live else "dry-run"}
    try:
        out["prepare"] = prepare(new_trial)
        out["dotenv_keys"] = _read_dotenv_keys()
        if args.dry_run:
            out["dry_run_checks"] = dry_run_checks(new_trial, out["prepare"])
            out["isolation_fix_check"] = isolation_fix_check(new_trial)
            out["VERDICT"] = "DRY-RUN-OK"
        else:
            out["live_recover"] = live_recover(new_trial)
            out["VERDICT"] = "LIVE-OK"
    except Exception as exc:  # noqa: BLE001
        out["exception"] = f"{type(exc).__name__}: {exc}"
        out["traceback"] = traceback.format_exc()
        out["VERDICT"] = "FAILED"

    print("\n===== RESULT =====")
    print(json.dumps(out, indent=2, default=str))
    return 0 if out.get("VERDICT", "").endswith("OK") else 1


if __name__ == "__main__":
    raise SystemExit(main())
