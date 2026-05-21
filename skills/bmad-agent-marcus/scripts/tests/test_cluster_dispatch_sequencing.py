from __future__ import annotations

from importlib import util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[4]
SCRIPT_PATH = ROOT / "skills" / "bmad-agent-marcus" / "scripts" / "cluster_dispatch_sequencing.py"
CONFIG_PATH = ROOT / "state" / "config" / "dispatch.yaml"


def _load_module():
    spec = util.spec_from_file_location("cluster_dispatch_sequencing", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    mod = util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


mod = _load_module()
generate_dispatch_plan = mod.generate_dispatch_plan
DispatchPlanError = mod.DispatchPlanError
load_dispatch_config = mod.load_dispatch_config


def _config():
    return load_dispatch_config(CONFIG_PATH)


def _clusters():
    return [
        {"cluster_id": "c1", "priority": 2, "size": 3},
        {"cluster_id": "c2", "priority": 1, "size": 5},
        {"cluster_id": "c3", "priority": 2, "size": 1},
    ]


def test_deterministic_order_and_hash():
    cfg = _config()
    plan1 = generate_dispatch_plan(_clusters(), config=cfg)
    plan2 = generate_dispatch_plan(_clusters(), config=cfg)
    assert plan1["steps"][0]["cluster_id"] == "c1"
    assert plan1["plan_hash"] == plan2["plan_hash"]


def test_batching_respects_batch_size():
    cfg = _config()
    cfg["policy"]["batch_size"] = 2
    plan = generate_dispatch_plan(_clusters(), config=cfg)
    assert plan["batches"] == 2  # 3 items -> batches of 2 => 2 batches
    assert plan["steps"][0]["batch_index"] == 0
    assert plan["steps"][-1]["batch_index"] == 1


def test_cycle_detection_raises():
    cfg = _config()
    cyc = [
        {"cluster_id": "c1", "priority": 1, "depends_on": ["c2"]},
        {"cluster_id": "c2", "priority": 1, "depends_on": ["c1"]},
    ]
    with pytest.raises(DispatchPlanError) as exc:
        generate_dispatch_plan(cyc, config=cfg)
    assert exc.value.code == "invalid_policy"


def test_missing_cluster_id_raises():
    cfg = _config()
    bad = [{"priority": 1}]
    with pytest.raises(DispatchPlanError) as exc:
        generate_dispatch_plan(bad, config=cfg)
    assert exc.value.code == "missing_required_field"


def test_retry_backoff_attached_per_step():
    cfg = _config()
    plan = generate_dispatch_plan(_clusters(), config=cfg)
    step = plan["steps"][0]
    assert step["attempts"]["max"] == cfg["retries"]["max_attempts"]
    assert step["attempts"]["backoff"]["initial"] == cfg["backoff"]["initial"]
    assert "idempotency_key" in step
