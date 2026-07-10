"""Mine-next trust Wave 1 liveproof: UDAC GATE_ASSET_MAP + reenter + join-collapse."""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from app.marcus.lesson_plan.run_asset_index import GATE_ASSET_MAP, DigestAlgo  # noqa: E402
from app.models.runtime.production_envelope import (  # noqa: E402
    ProductionEnvelope,
    SpecialistContribution,
    compute_output_digest,
)
from app.specialists.narration_join import (  # noqa: E402
    collapsed_segment_ids,
    join_narration_segments,
)
from datetime import datetime as dt  # noqa: E402
from uuid import UUID  # noqa: E402


def _bank(slug: str, lane: str, name: str, predicates: dict) -> tuple[Path, bool]:
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    run_id = str(uuid4())
    run_dir = REPO / "runs" / run_id
    run_dir.mkdir(parents=True)
    evidence = (
        REPO
        / "_bmad-output/implementation-artifacts/evidence"
        / f"{slug}-{stamp}"
    )
    item = evidence / name
    item.mkdir(parents=True)
    bool_keys = [k for k, v in predicates.items() if isinstance(v, bool)]
    passed = all(predicates[k] for k in bool_keys)
    verdict = {
        "lane": lane,
        "name": name,
        "passed": passed,
        "predicates": {**predicates, "run_id": run_id},
        "run_dir": str(run_dir),
    }
    (item / "verdict.json").write_text(
        json.dumps(verdict, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (item / "command-transcript.md").write_text(
        f"# {lane} {name}\n\npassed={passed}\n", encoding="utf-8"
    )
    (item / "PROOF.md").write_text(
        f"# PROOF {lane}\n\n{json.dumps(predicates, indent=2)}\n\nPASS={passed}\n",
        encoding="utf-8",
    )
    print(json.dumps(verdict, indent=2, sort_keys=True))
    return evidence, passed


def main() -> int:
    # T1 UDAC
    t1 = {
        "has_g0e": "G0E" in GATE_ASSET_MAP,
        "has_g0r": "G0R" in GATE_ASSET_MAP,
        "has_g1": GATE_ASSET_MAP.get("G1", ())[0].rel_path
        == "irene-pass1.lesson-plan.json"
        if "G1" in GATE_ASSET_MAP
        else False,
        "has_g2c": GATE_ASSET_MAP.get("G2C", ())[0].rel_path
        == "storyboard-publish-G2C.json"
        if "G2C" in GATE_ASSET_MAP
        else False,
        "has_g3": "G3" in GATE_ASSET_MAP,
        "g4_absent_honest": "G4" not in GATE_ASSET_MAP and "G4A" not in GATE_ASSET_MAP,
        "g1_canonical": GATE_ASSET_MAP["G1"][0].digest_algo is DigestAlgo.CANONICAL_SHA256
        if "G1" in GATE_ASSET_MAP
        else False,
    }
    _, p1 = _bank("mine-next-trust-t1-udac-map", "T1", "udac-gate-asset-map", t1)

    # T2 drop + reenter API surface
    trial_id = UUID("12345678-1234-4234-8234-123456789abc")
    env = ProductionEnvelope(trial_id=trial_id, fixture_run=True)
    for node_id, specialist in (("n1", "a"), ("n2", "b"), ("n3", "c")):
        output = {"node": node_id}
        env.add_contribution(
            SpecialistContribution(
                specialist_id=specialist,
                contributed_at=dt.now(UTC),
                output=output,
                cost_usd=0.0,
                model_used="fixture",
                output_digest=compute_output_digest(output),
                node_id=node_id,
                provenance="fixture",
            )
        )
    dropped = env.drop_contributions_from_nodes({"n2", "n3"})
    import inspect

    from app.marcus.orchestrator.production_runner import recover_production_trial

    sig = inspect.signature(recover_production_trial)
    t2 = {
        "drop_count_2": dropped == 2,
        "kept_n1_only": [c.node_id for c in env.contributions] == ["n1"],
        "api_has_reenter_at_node": "reenter_at_node" in sig.parameters,
        "negative_empty_drop_noop": env.drop_contributions_from_nodes(set()) == 0,
    }
    _, p2 = _bank("mine-next-trust-t2-reenter", "T2", "reenter-at-node", t2)

    # T3 collapse detector
    narration = [
        {"id": "seg-1", "narration_text": "First."},
        {"id": "seg-2", "narration_text": "Second."},
    ]
    bad_deltas = [
        {"id": "seg-1", "visual_references": [{"perception_source": "s1"}]},
        {"id": "seg-1", "visual_references": [{"perception_source": "s2"}]},
    ]
    good_deltas = [
        {"id": "seg-1", "visual_references": [{"perception_source": "s1"}]},
        {"id": "seg-2", "visual_references": [{"perception_source": "s2"}]},
    ]
    collapsed = collapsed_segment_ids(join_narration_segments(narration, bad_deltas))
    clean = collapsed_segment_ids(join_narration_segments(narration, good_deltas))
    from app.specialists.enrique import _act as enrique_act
    from app.marcus.orchestrator import storyboard_publisher

    t3 = {
        "detects_collapse": collapsed == ["seg-1"],
        "clean_empty": clean == [],
        "enrique_imports": enrique_act.collapsed_segment_ids is collapsed_segment_ids,
        "publisher_imports": (
            storyboard_publisher.collapsed_segment_ids is collapsed_segment_ids
        ),
        "negative_phantom_not_collapse": collapsed_segment_ids(
            [{"segment_id": "x", "narration_text": ""}]
        )
        == [],
    }
    _, p3 = _bank("mine-next-trust-t3-join-collapse", "T3", "join-collapse-detector", t3)

    return 0 if (p1 and p2 and p3) else 1


if __name__ == "__main__":
    raise SystemExit(main())
