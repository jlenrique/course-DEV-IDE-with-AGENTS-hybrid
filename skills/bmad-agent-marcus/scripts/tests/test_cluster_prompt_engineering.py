from __future__ import annotations

from importlib import util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[4]
SCRIPT_PATH = ROOT / "skills" / "bmad-agent-marcus" / "scripts" / "cluster_prompt_engineering.py"
CONFIG_PATH = ROOT / "state" / "config" / "prompting.yaml"


def _load_module():
    spec = util.spec_from_file_location("cluster_prompt_engineering", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    mod = util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


mod = _load_module()
render_prompt = mod.render_prompt
PromptEngineeringError = mod.PromptEngineeringError
load_prompt_config = mod.load_prompt_config


def _config():
    return load_prompt_config(CONFIG_PATH)


def _cluster_base():
    return {
        "cluster_id": "c-123",
        "goal": "Explain the mechanism of action clearly and concisely.",
        "intents": ["summarize", "clarify"],
        "constraints": {"visual_constraints": {"palette": "navy", "accent": "teal"}},
        "slides": [{"id": "s1"}, {"id": "s2"}, {"id": "s3"}],
    }


def test_happy_path_small_cluster():
    cfg = _config()
    res = render_prompt(_cluster_base(), config=cfg, seed="seed1")
    assert res["prompt_id"]
    assert "Cluster c-123" in res["prompt_text"]
    assert res["audit"]["constraints_applied"] is True
    assert res["audit"]["token_budget_used"] <= res["audit"]["token_budget_max"]


def test_missing_required_field_raises():
    cfg = _config()
    bad = _cluster_base()
    bad.pop("goal", None)
    with pytest.raises(PromptEngineeringError) as exc:
        render_prompt(bad, config=cfg)
    assert exc.value.code == "missing_required_field"


def test_safety_violation_blocks():
    cfg = _config()
    bad = _cluster_base()
    bad["goal"] = "Discuss handling of credit card information."
    with pytest.raises(PromptEngineeringError) as exc:
        render_prompt(bad, config=cfg)
    assert exc.value.code == "safety_violation"


def test_budget_guard_blocks_when_exceeded():
    cfg = _config()
    cfg = {**cfg, "token_budget": {"max_per_prompt": 5}}
    bad = _cluster_base()
    with pytest.raises(PromptEngineeringError) as exc:
        render_prompt(bad, config=cfg)
    assert exc.value.code == "prompt_over_budget"


def test_deterministic_with_seed():
    cfg = _config()
    cluster = _cluster_base()
    res1 = render_prompt(cluster, config=cfg, seed="same-seed")
    res2 = render_prompt(cluster, config=cfg, seed="same-seed")
    assert res1["prompt_id"] == res2["prompt_id"]
    assert res1["prompt_text"] == res2["prompt_text"]


def test_graceful_without_visual_constraints():
    cfg = _config()
    cluster = _cluster_base()
    cluster["constraints"] = {}
    res = render_prompt(cluster, config=cfg, seed="novisual")
    assert "visual constraints not provided" in res["prompt_text"]
    assert res["audit"]["constraints_applied"] is False
