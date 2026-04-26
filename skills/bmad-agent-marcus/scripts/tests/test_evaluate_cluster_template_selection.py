from __future__ import annotations

import json
from importlib import util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
SCRIPT_PATH = ROOT / "skills" / "bmad-agent-marcus" / "scripts" / "evaluate_cluster_template_selection.py"


def _load_module():
    spec = util.spec_from_file_location("evaluate_cluster_template_selection", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    mod = util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


mod = _load_module()


def _write_bundle(
    bundle: Path,
    *,
    slide_count: int,
    missing_assets: int,
    cluster_groups: int,
    interstitials: int,
    include_template_plan: bool,
    include_selected_template_ids: bool,
) -> None:
    bundle.mkdir(parents=True, exist_ok=True)
    (bundle / "storyboard").mkdir(parents=True, exist_ok=True)

    authorized = {
        "slide_ids": [f"s-{i}" for i in range(1, slide_count + 1)],
        "authorized_slides": [
            {"slide_id": f"s-{i}", "card_number": i, "file_path": f"slide-{i:02d}.png", "source_ref": f"src#{i}"}
            for i in range(1, slide_count + 1)
        ],
    }
    slides = []
    for i in range(1, slide_count + 1):
        role = "interstitial" if i <= interstitials else "head"
        row = {"slide_id": f"s-{i}", "card_number": i, "cluster_role": role, "narration_status": "present"}
        if include_selected_template_ids and cluster_groups > 0:
            row["selected_template_id"] = "deep-dive"
        slides.append(row)

    storyboard = {
        "slides": slides,
        "cluster_groups": [{"cluster_id": f"c-{i}"} for i in range(1, cluster_groups + 1)],
        "review_meta": {"missing_assets": missing_assets, "double_dispatch_enabled": False},
    }

    envelope = {}
    if include_template_plan:
        envelope = {
            "cluster_template_plan": {
                "schema_version": "1.0",
                "clusters": [{"cluster_id": "c-1", "selected_template_id": "deep-dive"}],
                "selected_template_ids_by_cluster": {"c-1": "deep-dive"},
            }
        }

    (bundle / "authorized-storyboard.json").write_text(json.dumps(authorized), encoding="utf-8")
    (bundle / "storyboard" / "storyboard.json").write_text(json.dumps(storyboard), encoding="utf-8")
    if envelope:
        (bundle / "pass2-envelope.json").write_text(json.dumps(envelope), encoding="utf-8")


def test_compare_emits_expected_shape(tmp_path: Path) -> None:
    baseline = tmp_path / "baseline"
    candidate = tmp_path / "candidate"
    _write_bundle(
        baseline,
        slide_count=2,
        missing_assets=0,
        cluster_groups=0,
        interstitials=0,
        include_template_plan=False,
        include_selected_template_ids=False,
    )
    _write_bundle(
        candidate,
        slide_count=3,
        missing_assets=0,
        cluster_groups=1,
        interstitials=1,
        include_template_plan=True,
        include_selected_template_ids=True,
    )

    report = mod.compare_c1_m1_runs(
        lesson_id="C1-M1",
        baseline_bundle=baseline,
        candidate_bundle=candidate,
    )

    assert report["artifact_type"] == "c1-m1-comparative-evaluation"
    assert report["lesson_id"] == "C1-M1"
    assert report["delta"]["cluster_group_count"] == 1
    assert report["delta"]["interstitial_slide_count"] == 1
    assert report["decision"]["status"] in {"pass", "warn", "fail"}


def test_compare_fails_when_missing_assets_regress(tmp_path: Path) -> None:
    baseline = tmp_path / "baseline"
    candidate = tmp_path / "candidate"
    _write_bundle(
        baseline,
        slide_count=2,
        missing_assets=0,
        cluster_groups=0,
        interstitials=0,
        include_template_plan=False,
        include_selected_template_ids=False,
    )
    _write_bundle(
        candidate,
        slide_count=2,
        missing_assets=2,
        cluster_groups=1,
        interstitials=1,
        include_template_plan=True,
        include_selected_template_ids=True,
    )

    report = mod.compare_c1_m1_runs(
        lesson_id="C1-M1",
        baseline_bundle=baseline,
        candidate_bundle=candidate,
    )

    assert report["decision"]["status"] == "fail"
    assert "candidate_missing_assets_exceed_baseline" in report["decision"]["reasons"]


def test_compare_fails_when_cluster_template_plan_missing_for_clustered_candidate(tmp_path: Path) -> None:
    baseline = tmp_path / "baseline"
    candidate = tmp_path / "candidate"
    _write_bundle(
        baseline,
        slide_count=2,
        missing_assets=0,
        cluster_groups=0,
        interstitials=0,
        include_template_plan=False,
        include_selected_template_ids=False,
    )
    _write_bundle(
        candidate,
        slide_count=2,
        missing_assets=0,
        cluster_groups=1,
        interstitials=1,
        include_template_plan=False,
        include_selected_template_ids=False,
    )

    report = mod.compare_c1_m1_runs(
        lesson_id="C1-M1",
        baseline_bundle=baseline,
        candidate_bundle=candidate,
    )

    assert report["decision"]["status"] == "fail"
    assert "cluster_groups_present_without_template_cluster_plan" in report["decision"]["reasons"]


def test_write_artifact_persists_json(tmp_path: Path) -> None:
    baseline = tmp_path / "baseline"
    candidate = tmp_path / "candidate"
    _write_bundle(
        baseline,
        slide_count=1,
        missing_assets=0,
        cluster_groups=0,
        interstitials=0,
        include_template_plan=False,
        include_selected_template_ids=False,
    )
    _write_bundle(
        candidate,
        slide_count=1,
        missing_assets=0,
        cluster_groups=0,
        interstitials=0,
        include_template_plan=False,
        include_selected_template_ids=False,
    )

    report = mod.compare_c1_m1_runs(
        lesson_id="C1-M1",
        baseline_bundle=baseline,
        candidate_bundle=candidate,
    )
    output = tmp_path / "out" / "comparative.json"
    written = mod.write_artifact(report, output)

    assert written.is_file()
    persisted = json.loads(written.read_text(encoding="utf-8"))
    assert persisted["artifact_version"] == 1

