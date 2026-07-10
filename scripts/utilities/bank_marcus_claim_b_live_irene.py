"""Live Claim B proof: Marcus solicitation → live Irene Pass-1 on runs/<uuid>/.

Banks treatment (with ratification) vs control (absent) under a real runs/
consumer root. Uses make_chat_model (OPENAI_API_KEY from .env).
"""

from __future__ import annotations

import hashlib
import json
import shutil
import sys
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from scripts.utilities.env_loader import load_env  # noqa: E402

load_env(REPO / ".env")

from app.marcus.cli.plan_ratify_cli import main as plan_ratify_main  # noqa: E402
from app.marcus.lesson_plan.planning_context import load_planning_context  # noqa: E402
from app.models.state.cache_state import CacheState  # noqa: E402
from app.models.state.run_state import RunState  # noqa: E402
from app.specialists.irene_pass1 import graph as pass1_graph  # noqa: E402

TEJAL = REPO / "course-content/courses/tejal-c1m1-p4-assessments-bridge"
PURPOSE = (
    "Bridge Module-1 innovator-mindset into Module-2 leadership-identity "
    "with assessment-driven reflection checkpoints"
)
AUDIENCE = (
    "APC Cohort-C1 clinician-innovators preparing for Module-2 "
    "leadership-identity work"
)
LO_STATEMENT = (
    "Map Module-1 Opportunity-Radar targets onto Module-2 "
    "leadership-identity competencies using assessment-bridge language"
)


def _build_extracted_md(dest: Path) -> Path:
    dest.mkdir(parents=True, exist_ok=True)
    parts: list[str] = ["# Tejal C1M1 Part 4 — Assessments Bridge\n"]
    for rel in (
        "slides/slide-1-summary-bridge-to-module-2.md",
        "references/module-1-core-conceptual-pillars.md",
        "assessments/comprehensive-module-knowledge-check.md",
    ):
        src = TEJAL / rel
        if src.is_file():
            parts.append(f"\n## Source: {rel}\n")
            parts.append(src.read_text(encoding="utf-8"))
    path = dest / "extracted.md"
    path.write_text("\n".join(parts), encoding="utf-8")
    return path


def _state(payload: dict) -> RunState:
    return RunState(
        graph_version="v0.1-stub",
        temperature=0.3,
        cache_state=CacheState(
            cache_prefix=json.dumps(payload, sort_keys=True),
            entries_count=0,
        ),
    )


def _run_pass1(*, run_id: str, runs_root: Path, bundle: Path, with_context: bool) -> dict:
    payload: dict = {
        "mode": "pass-1",
        "run_id": run_id,
        "runs_root": str(runs_root),
        "bundle_reference": str(bundle),
    }
    if with_context:
        ctx = load_planning_context(runs_root / run_id)
        if ctx is None:
            raise RuntimeError(f"expected planning_context under {runs_root / run_id}")
        payload["planning_context"] = ctx.to_payload_dict()
    state = _state(payload)
    plan_update = pass1_graph._plan(state)
    state = state.model_copy(update=plan_update)
    act_update = pass1_graph._act(state)
    return json.loads(act_update["cache_state"]["cache_prefix"])


def main() -> int:
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    evidence = (
        REPO
        / "_bmad-output/implementation-artifacts/evidence"
        / f"marcus-claim-b-live-{stamp}"
    )
    evidence.mkdir(parents=True, exist_ok=True)

    runs_root = REPO / "runs"
    treatment_id = str(uuid4())
    control_id = str(uuid4())
    treatment_dir = runs_root / treatment_id
    control_dir = runs_root / control_id
    treatment_dir.mkdir(parents=True)
    control_dir.mkdir(parents=True)

    # --- Claim A seed into real RUN_DIR ---
    rc = plan_ratify_main(
        [
            "--purpose",
            PURPOSE,
            "--audience",
            AUDIENCE,
            "--workflow",
            "narrated-deck",
            "--gap-fill-chosen",
            "lighter_collateral",
            "--gap-fill-considered",
            "lighter_collateral,wait,synthesize",
            "--gap-fill-rationale",
            "Ship deck now; defer motion",
            "--output-dir",
            str(treatment_dir),
            "--corpus-dir",
            str(TEJAL),
        ]
    )
    if rc != 0:
        raise SystemExit(f"plan-ratify failed: {rc}")

    (treatment_dir / "ratified-los.json").write_text(
        json.dumps(
            {
                "ratified_los": [
                    {
                        "objective_id": "lo-bridge-001",
                        "statement": LO_STATEMENT,
                        "bloom_level": "apply",
                        "status": "ratified",
                    }
                ]
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    bundle_t = treatment_dir / "bundle"
    bundle_c = control_dir / "bundle"
    _build_extracted_md(bundle_t)
    shutil.copytree(bundle_t, bundle_c)

    print(f"TREATMENT_RUN={treatment_id}")
    print(f"CONTROL_RUN={control_id}")
    print("Invoking live Irene Pass-1 treatment…")
    treatment = _run_pass1(
        run_id=treatment_id,
        runs_root=runs_root,
        bundle=bundle_t,
        with_context=True,
    )
    print("Invoking live Irene Pass-1 control…")
    control = _run_pass1(
        run_id=control_id,
        runs_root=runs_root,
        bundle=bundle_c,
        with_context=False,
    )

    t_plan_path = Path(treatment["artifact_path"])
    c_plan_path = Path(control["artifact_path"])
    t_hash = hashlib.sha256(t_plan_path.read_bytes()).hexdigest()
    c_hash = hashlib.sha256(c_plan_path.read_bytes()).hexdigest()
    coverage = treatment.get("planning_context_coverage")
    provenance = treatment.get("lesson_plan", {}).get("planning_provenance")
    plan_text = t_plan_path.read_text(encoding="utf-8").lower()

    predicates = {
        "consumer_root_is_runs_uuid": str(treatment_dir).replace("\\", "/").endswith(
            f"runs/{treatment_id}"
        )
        or treatment_dir.resolve().parent.name == "runs",
        "ratification_present": (treatment_dir / "planning-ratification.json").is_file(),
        "intent_present": (
            treatment_dir / "ratified-collateral-intent.yaml"
        ).is_file(),
        "los_present": (treatment_dir / "ratified-los.json").is_file(),
        "irene_pass1_md_treatment": t_plan_path.is_file(),
        "irene_pass1_md_control": c_plan_path.is_file(),
        "plan_hash_differs": t_hash != c_hash,
        "coverage_present": isinstance(coverage, dict),
        "lo_coverage": (coverage or {}).get("lo_coverage"),
        "purpose_acknowledged": (coverage or {}).get("purpose_acknowledged"),
        "audience_acknowledged": (coverage or {}).get("audience_acknowledged"),
        "provenance_present": isinstance(provenance, dict),
        "provenance_digest": (provenance or {}).get("ratification_digest"),
        "control_omits_coverage": "planning_context_coverage" not in control,
        "control_omits_provenance": "planning_provenance"
        not in control.get("lesson_plan", {}),
        "purpose_token_in_plan": "leadership-identity" in plan_text
        or "assessment" in plan_text,
        "lo_token_in_plan": "opportunity-radar" in plan_text
        or "leadership-identity" in plan_text,
        "treatment_run_id": treatment_id,
        "control_run_id": control_id,
        "treatment_plan_hash": t_hash,
        "control_plan_hash": c_hash,
    }

    required = [
        "consumer_root_is_runs_uuid",
        "ratification_present",
        "intent_present",
        "irene_pass1_md_treatment",
        "irene_pass1_md_control",
        "plan_hash_differs",
        "coverage_present",
        "provenance_present",
        "control_omits_coverage",
        "control_omits_provenance",
    ]
    failed = [k for k in required if not predicates.get(k)]
    lo_cov = predicates["lo_coverage"]
    bespoke_ok = lo_cov in {"partial", "present"} and predicates["lo_token_in_plan"]
    framing_ok = bool(predicates["purpose_acknowledged"]) and bool(
        predicates["audience_acknowledged"]
    )

    claim = "FAIL"
    if not failed and framing_ok:
        claim = "PASS-bespoke" if bespoke_ok else "PASS-framing-only"
    elif not failed:
        claim = "PASS-partial-ack-weak"

    # Mirror into evidence
    mirror_t = evidence / "treatment"
    mirror_c = evidence / "control"
    mirror_t.mkdir(parents=True)
    mirror_c.mkdir(parents=True)
    for name in (
        "planning-ratification.json",
        "ratified-collateral-intent.yaml",
        "ratified-los.json",
        "irene-pass1.md",
        "planning-context-coverage.json",
    ):
        src = treatment_dir / name
        if src.is_file():
            shutil.copy2(src, mirror_t / name)
    if t_plan_path.is_file():
        shutil.copy2(t_plan_path, mirror_t / "irene-pass1.md")
    if c_plan_path.is_file():
        shutil.copy2(c_plan_path, mirror_c / "irene-pass1.md")
    (evidence / "treatment-output.json").write_text(
        json.dumps(treatment, indent=2, default=str), encoding="utf-8"
    )
    (evidence / "control-output.json").write_text(
        json.dumps(control, indent=2, default=str), encoding="utf-8"
    )
    (evidence / "predicates.json").write_text(
        json.dumps(
            {
                "claim": claim,
                "failed_required": failed,
                "framing_ok": framing_ok,
                "bespoke_ok": bespoke_ok,
                "predicates": predicates,
                "purpose": PURPOSE,
                "audience": AUDIENCE,
                "lo_statement": LO_STATEMENT,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    proof = f"""# PROOF — Claim B LIVE Irene Pass-1

**Stamp:** {stamp}
**Status:** {claim}
**TREATMENT_RUN:** `runs/{treatment_id}/`
**CONTROL_RUN:** `runs/{control_id}/`

## Required predicates
{json.dumps({k: predicates[k] for k in required}, indent=2)}

## Ack / LO
- framing_ok: {framing_ok}
- bespoke_ok: {bespoke_ok}
- lo_coverage: {lo_cov}
- purpose_acknowledged: {predicates['purpose_acknowledged']}
- audience_acknowledged: {predicates['audience_acknowledged']}

## Failed required
{failed or '(none)'}

## Non-claims
Gamma spend not invoked. SPOC REPL not claimed. This is live OpenAI Pass-1 emit proof.
"""
    (evidence / "PROOF.md").write_text(proof, encoding="utf-8")
    print(json.dumps({"claim": claim, "failed": failed, "evidence": str(evidence)}, indent=2))
    return 0 if claim.startswith("PASS") and not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
