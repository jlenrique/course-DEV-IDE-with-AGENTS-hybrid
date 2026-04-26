from __future__ import annotations

from importlib import util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[4]
SCRIPT_PATH = ROOT / "skills" / "bmad-agent-marcus" / "scripts" / "cluster_coherence_validation.py"
CONFIG_PATH = ROOT / "state" / "config" / "validation.yaml"


def _load_module():
    spec = util.spec_from_file_location("cluster_coherence_validation", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    mod = util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


mod = _load_module()
validate_cluster = mod.validate_cluster
validate_interstitial_replacement = mod.validate_interstitial_replacement
CoherenceValidationError = mod.CoherenceValidationError
load_validation_config = mod.load_validation_config


def _config():
    return load_validation_config(CONFIG_PATH)


def _manifest():
    return {
        "segments": [
            {"slide_id": "s1"},
            {"slide_id": "s2"},
        ]
    }


def _outputs_ok():
    return [
        {"slide_id": "s1", "text": "Mechanism overview with coherent safety baseline."},
        {"slide_id": "s2", "text": "Detailed steps remain coherent and aligned."},
    ]


def test_pass_happy_path():
    cfg = _config()
    report = validate_cluster(manifest=_manifest(), outputs=_outputs_ok(), constraints={"required_terms": ["coherent"]}, config=cfg, seed="seedA")
    assert report["decision"] == "pass"
    assert report["report_hash"]


def test_missing_output_fails():
    cfg = _config()
    outs = [{"slide_id": "s1", "text": "Only one slide present."}]
    report = validate_cluster(manifest=_manifest(), outputs=outs, config=cfg)
    assert report["decision"] == "fail"
    assert any("missing_output" in v for v in report["violations"])


def test_ordering_violation_flags():
    cfg = _config()
    outs = list(reversed(_outputs_ok()))
    report = validate_cluster(manifest=_manifest(), outputs=outs, config=cfg)
    assert "ordering_mismatch" in report["violations"]


def test_forbidden_term_flags():
    cfg = _config()
    outs = _outputs_ok()
    outs[0]["text"] = "This contains conflict which is forbidden."
    report = validate_cluster(manifest=_manifest(), outputs=outs, constraints={"forbidden_terms": ["conflict"]}, config=cfg)
    assert any("forbidden_term" in v for v in report["violations"])


def test_invalid_outputs_type_raises():
    cfg = _config()
    with pytest.raises(CoherenceValidationError) as exc:
        validate_cluster(manifest=_manifest(), outputs={"bad": "data"}, config=cfg)
    assert exc.value.code == "invalid_output_format"


def test_interstitial_replacement_pass_happy_path():
    cfg = _config()
    report = validate_interstitial_replacement(
        head_output={"slide_id": "head-1", "text": "Coherent base context."},
        replacement_output={"slide_id": "int-2", "text": "Coherent interstitial bridge."},
        constraints={"required_terms": ["coherent"]},
        config=cfg,
        seed="seedB",
    )
    assert report["decision"] == "pass"
    assert report["report_hash"]


def test_interstitial_replacement_requires_slide_ids():
    cfg = _config()
    with pytest.raises(CoherenceValidationError) as exc:
        validate_interstitial_replacement(
            head_output={"text": "missing id"},
            replacement_output={"slide_id": "int-2", "text": "ok"},
            config=cfg,
        )
    assert exc.value.code == "missing_required_field"
