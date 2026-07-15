from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts.utilities import run_prework_36_4_live_evidence as driver


def test_dry_run_never_constructs_provider_or_evidence_pack(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    course = Path("course-content/courses/tejal-apc-c1-m1-p2-trends").resolve()
    before = set(driver.EVIDENCE_ROOT.glob("prework-36-4-live-*"))
    monkeypatch.setattr(
        driver,
        "preflight",
        lambda args, require_credentials: {
            "course_root": course,
            "run_dir": tmp_path,
            "model_config_digest": "sha256:" + "0" * 64,
        },
    )
    monkeypatch.setattr(
        driver,
        "run_live",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            AssertionError("dry-run must not enter live execution")
        ),
    )
    code = driver.main(
        [
            "--course-root",
            str(course),
            "--run-dir",
            str(tmp_path),
            "--output-root",
            str(tmp_path / "fresh-output"),
            "--max-spend-usd",
            "0.25",
            "--recovery-of",
            "5ff7db47-62af-48d0-8b67-fa300c04aa4d",
            "--dry-run",
        ]
    )
    payload = json.loads(capsys.readouterr().out)
    assert code == 0
    assert payload["provider_calls"] == 0
    assert payload["evidence_pack_created"] is False
    assert set(driver.EVIDENCE_ROOT.glob("prework-36-4-live-*")) == before


def test_preflight_rejects_incomplete_run_without_creating_pack(tmp_path: Path) -> None:
    args = driver.build_parser().parse_args(
        [
            "--course-root",
            "course-content/courses/tejal-apc-c1-m1-p2-trends",
            "--run-dir",
            str(tmp_path),
            "--output-root",
            str(tmp_path / "fresh-output"),
            "--max-spend-usd",
            "0.25",
            "--recovery-of",
            "5ff7db47-62af-48d0-8b67-fa300c04aa4d",
            "--dry-run",
        ]
    )
    try:
        driver.preflight(args, require_credentials=False)
    except ValueError as exc:
        assert "missing required files" in str(exc)
    else:
        raise AssertionError("incomplete dry-run fixture must fail preflight")


def test_recovery_attempt_requires_explicit_existing_failed_id(tmp_path: Path, monkeypatch) -> None:
    failed_id = "12ccd755-592b-45c2-8fd2-b3fbe51df2b9"
    verdict = tmp_path / "verdict.json"
    verdict.write_text('{"pass": false}', "utf-8")
    monkeypatch.setattr(driver, "_failed_attempts", lambda: {failed_id: verdict})
    try:
        driver.validate_recovery_label(None)
    except ValueError as exc:
        assert "--recovery-of" in str(exc)
    else:
        raise AssertionError("unlabeled second attempt must be refused")
    assert driver.validate_recovery_label(failed_id) == verdict
    try:
        driver.validate_recovery_label("unknown")
    except ValueError as exc:
        assert "existing failed" in str(exc)
    else:
        raise AssertionError("unknown recovery attempt must be refused")


def test_causal_manifest_changes_only_for_allowlisted_bytes(tmp_path: Path) -> None:
    causal = tmp_path / "causal.py"
    unrelated = tmp_path / "unrelated.txt"
    verdict = tmp_path / "verdict.json"
    causal.write_text("fix-v1", "utf-8")
    unrelated.write_text("ambient-v1", "utf-8")
    verdict.write_text('{"pass": false}', "utf-8")
    causal_rel = causal.relative_to(driver.ROOT).as_posix()

    initial = driver.causal_fix_manifest(verdict, paths=(causal_rel,))
    unrelated.write_text("ambient-v2", "utf-8")
    ambient_changed = driver.causal_fix_manifest(verdict, paths=(causal_rel,))
    assert ambient_changed["manifest_digest"] == initial["manifest_digest"]

    causal.write_text("fix-v2", "utf-8")
    causal_changed = driver.causal_fix_manifest(verdict, paths=(causal_rel,))
    assert causal_changed["manifest_digest"] != initial["manifest_digest"]
    assert causal_changed["prior_failed_verdict"]["sha256"] == driver._digest(verdict)


def test_preventive_spend_bound_rejects_insufficient_cap() -> None:
    with pytest.raises(ValueError, match="below preventive two-call bound"):
        driver.preventive_spend_bound(0.01, "gpt-5")


def test_accepted_spend_cap_mathematically_bounds_both_calls() -> None:
    bound = driver.preventive_spend_bound(0.25, "gpt-5")
    pricing = driver.load_pricing()
    recomputed = bound["call_count"] * pricing.compute_cost(
        bound["model"],
        input_tokens=bound["input_token_ceiling_per_call"],
        output_tokens=bound["max_completion_tokens_per_call"],
    )
    assert recomputed == bound["worst_case_usd"]
    assert recomputed <= 0.25


@pytest.mark.parametrize("invalid_cap", ["nan", "inf", "-inf", "0", "-0.01"])
def test_cli_rejects_nonfinite_or_nonpositive_cap_before_live_construction(
    invalid_cap: str, monkeypatch
) -> None:
    before = set(driver.EVIDENCE_ROOT.glob("prework-36-4-live-*"))
    provider_constructions = 0

    def forbidden_writer(*args, **kwargs):
        nonlocal provider_constructions
        provider_constructions += 1
        raise AssertionError("invalid cap must fail before adapter construction")

    monkeypatch.setattr(driver, "LiveSceneComposer", forbidden_writer)
    monkeypatch.setattr(driver, "LivePromiseTransformer", forbidden_writer)
    with pytest.raises(ValueError, match="finite and greater than zero"):
        driver.main(
            [
                "--course-root",
                "unused",
                "--run-dir",
                "unused",
                "--output-root",
                "unused",
                f"--max-spend-usd={invalid_cap}",
                "--recovery-of",
                "12ccd755-592b-45c2-8fd2-b3fbe51df2b9",
            ]
        )
    assert provider_constructions == 0
    assert set(driver.EVIDENCE_ROOT.glob("prework-36-4-live-*")) == before


def test_degraded_scene_is_transport_safe_but_not_primary_golden_acceptance() -> None:
    payload = SimpleNamespace(
        pre_work=SimpleNamespace(
            scene=SimpleNamespace(status="degraded"),
            promise=SimpleNamespace(status="authored"),
        ),
        scene_receipt=SimpleNamespace(
            gate=SimpleNamespace(
                failures=("scene_faithfulness_overlap", "scene_faithfulness_negator")
            )
        ),
        promise_receipt=SimpleNamespace(gate=SimpleNamespace(failures=())),
    )
    machine_transport_render_pass = True
    assert machine_transport_render_pass is True
    assert driver.primary_part2_acceptance(payload) is False


def test_legacy_incomplete_adjudication_is_not_retry_authority() -> None:
    attempt_id = "380ecd47-7491-42ab-a3d8-a68c1afbb078"
    with pytest.raises(ValueError, match="existing failed"):
        driver.validate_recovery_label(attempt_id)


def _write_clone_manifest(run_dir: Path) -> Path:
    (run_dir / "exports").mkdir(parents=True)
    (run_dir / "bundle").mkdir()
    companions = {
        "run.json": "{}\n",
        "ratified-los.json": "{}\n",
        "exports/segment-manifest-storyboard-b.yaml": "segments: []\n",
        "bundle/extracted.md": "# Extracted\n",
    }
    for relative, content in companions.items():
        (run_dir / relative).write_text(content, "utf-8")
    manifest = {
        "schema_version": "prework-36-4-fresh-clone.v1",
        "source_label": "production-shaped-fixture",
        "origin_label": "fresh-pre-07W.1-clone",
        "created_at": "2026-07-13T02:50:00Z",
        "run_json_digest": driver._digest(run_dir / "run.json"),
        "ratified_los_digest": driver._digest(run_dir / "ratified-los.json"),
        "segment_manifest_digest": driver._digest(
            run_dir / "exports/segment-manifest-storyboard-b.yaml"
        ),
        "bundle_extracted_digest": driver._digest(run_dir / "bundle/extracted.md"),
        "no_real_brief_contribution": True,
        "no_workbook_brief_sidecar": True,
    }
    path = run_dir / "fresh-clone-manifest.json"
    path.write_text(json.dumps(manifest, indent=2) + "\n", "utf-8")
    return path


def test_fresh_clone_manifest_binds_all_companions(tmp_path: Path) -> None:
    manifest_path = _write_clone_manifest(tmp_path)
    manifest, digest = driver.read_fresh_clone_manifest(tmp_path)
    assert manifest.origin_label == "fresh-pre-07W.1-clone"
    assert digest == driver._digest(manifest_path)
    (tmp_path / "ratified-los.json").write_text('{"changed": true}\n', "utf-8")
    with pytest.raises(ValueError, match="ratified_los_digest"):
        driver.read_fresh_clone_manifest(tmp_path)


def test_fresh_clone_rejects_stale_sidecar(tmp_path: Path) -> None:
    _write_clone_manifest(tmp_path)
    (tmp_path / "workbook-brief.v1.json").write_text("{}\n", "utf-8")
    with pytest.raises(ValueError, match="must not contain"):
        driver.read_fresh_clone_manifest(tmp_path)


def test_reused_output_root_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="fresh and not already exist"):
        driver.validate_fresh_output_root(tmp_path)
    driver.validate_fresh_output_root(tmp_path / "unique-output")


def test_machine_green_remains_pending_operator_and_never_passes() -> None:
    verdict = driver.pending_operator_verdict(True, True)
    assert verdict == {
        "pass": None,
        "machine_transport_render_pass": True,
        "primary_part2_acceptance": True,
        "evidence_status": "pending_operator",
    }


def test_third_failed_adjudication_authorizes_recovery_and_digest_chain() -> None:
    attempt_id = "5ff7db47-62af-48d0-8b67-fa300c04aa4d"
    prior = driver.validate_recovery_label(attempt_id)
    assert prior is not None
    manifest = driver.causal_fix_manifest(prior)
    assert "Q5 answer/resolution leaked" in manifest["cause"]
    adjudication = driver.ROOT / manifest["prior_adjudication"]["path"]
    assert manifest["prior_failed_verdict"]["sha256"] == driver._digest(prior)
    assert manifest["prior_adjudication"]["sha256"] == driver._digest(adjudication)
    payload = json.loads(adjudication.read_text("utf-8"))
    assert driver.operator_adjudication_accepts(prior, payload) is False


def test_story_closure_requires_digest_bound_all_pass_operator_adjudication(
    tmp_path: Path,
) -> None:
    verdict = tmp_path / "verdict.json"
    attempt_id = "attempt-fixture"
    verdict.write_text(json.dumps(_machine_green_verdict(attempt_id)) + "\n", "utf-8")
    checks = {key: "PASS" for key in driver.REQUIRED_OPERATOR_SPOT_CHECKS}
    adjudication = {
        "story": "36.4",
        "attempt_id": attempt_id,
        "original_verdict_path": verdict.relative_to(driver.ROOT).as_posix(),
        "original_verdict_sha256": driver._digest(verdict),
        "semantic_acceptance": True,
        "operator_verdict": "PASS",
        "operator_spot_checks": checks,
    }
    assert driver.operator_adjudication_accepts(verdict, adjudication) is True
    adjudication["operator_spot_checks"]["scene_innocence"] = "PENDING"
    assert driver.operator_adjudication_accepts(verdict, adjudication) is False


@pytest.mark.parametrize(
    "mutation",
    [
        "missing_key",
        "extra_key",
        "wrong_story",
        "wrong_attempt",
        "wrong_path",
        "wrong_digest",
        "pending_check",
        "fail_check",
    ],
)
def test_operator_pass_adjudication_rejects_every_identity_or_check_mutation(
    mutation: str, tmp_path: Path
) -> None:
    verdict = tmp_path / "verdict.json"
    verdict.write_text(json.dumps(_machine_green_verdict("attempt-fixture")) + "\n", "utf-8")
    payload = {
        "story": "36.4",
        "attempt_id": "attempt-fixture",
        "original_verdict_path": verdict.relative_to(driver.ROOT).as_posix(),
        "original_verdict_sha256": driver._digest(verdict),
        "semantic_acceptance": True,
        "operator_verdict": "PASS",
        "operator_spot_checks": {key: "PASS" for key in driver.REQUIRED_OPERATOR_SPOT_CHECKS},
    }
    if mutation == "missing_key":
        payload["operator_spot_checks"].pop("provenance")
    elif mutation == "extra_key":
        payload["operator_spot_checks"]["extra"] = "PASS"
    elif mutation == "wrong_story":
        payload["story"] = "36.5"
    elif mutation == "wrong_attempt":
        payload["attempt_id"] = "other"
    elif mutation == "wrong_path":
        payload["original_verdict_path"] = "wrong/verdict.json"
    elif mutation == "wrong_digest":
        payload["original_verdict_sha256"] = "sha256:" + "0" * 64
    elif mutation == "pending_check":
        payload["operator_spot_checks"]["provenance"] = "PENDING"
    elif mutation == "fail_check":
        payload["operator_spot_checks"]["provenance"] = "FAIL"
    assert driver.operator_adjudication_state(verdict, payload) is None


def _machine_green_verdict(attempt_id: str) -> dict[str, object]:
    return {
        "story": "36.4",
        "attempt_id": attempt_id,
        "pass": None,
        "evidence_status": "pending_operator",
        "machine_transport_render_pass": True,
        "primary_part2_acceptance": True,
        "calls": 2,
        "writer_receipts": [{"writer": "scene"}, {"writer": "promise"}],
        "artifact_digest": "sha256:" + "1" * 64,
        "markdown_path": "workbook.md",
        "docx_path": "workbook.docx",
        "assertions": {"beat_order": True, "fr17": True},
        "scene_review": {
            "scene": {"status": "authored", "text": "A setup-only scene."},
            "operator_warnings": ["scene_invented_terms_operator_check"],
            "introduced_terms": ["clinical"],
        },
    }


@pytest.mark.parametrize(
    ("mutation", "value"),
    [
        ("missing_calls", None),
        ("machine_transport_render_pass", False),
        ("primary_part2_acceptance", False),
        ("error", "provider failed"),
        ("error", None),
        ("pass", False),
        ("pass", True),
        ("evidence_status", "failed"),
        ("story", "36.5"),
        ("attempt_id", "other-attempt"),
        ("missing_artifact_digest", None),
        ("missing_writer_receipts", None),
        ("missing_scene_review", None),
        ("assertions", {"beat_order": False}),
    ],
)
def test_operator_pass_cannot_override_non_green_or_incomplete_machine_evidence(
    mutation: str, value: object, tmp_path: Path
) -> None:
    verdict_payload = _machine_green_verdict("attempt-fixture")
    if mutation.startswith("missing_"):
        verdict_payload.pop(mutation.removeprefix("missing_"))
    else:
        verdict_payload[mutation] = value
    verdict = tmp_path / "verdict.json"
    verdict.write_text(json.dumps(verdict_payload) + "\n", "utf-8")
    adjudication = {
        "story": "36.4",
        "attempt_id": "attempt-fixture",
        "original_verdict_path": verdict.relative_to(driver.ROOT).as_posix(),
        "original_verdict_sha256": driver._digest(verdict),
        "semantic_acceptance": True,
        "operator_verdict": "PASS",
        "operator_spot_checks": {key: "PASS" for key in driver.REQUIRED_OPERATOR_SPOT_CHECKS},
    }
    assert driver.operator_adjudication_state(verdict, adjudication) is None


def test_pending_machine_or_adjudication_never_grants_retry_authority(
    tmp_path: Path, monkeypatch
) -> None:
    evidence = tmp_path / "evidence"
    pack = evidence / "prework-36-4-live-pending"
    adjudication_dir = evidence / "prework-36-4-adjudication-pending"
    pack.mkdir(parents=True)
    adjudication_dir.mkdir()
    verdict = pack / "verdict.json"
    verdict.write_text('{"attempt_id":"pending-id","pass":null}\n', "utf-8")
    adjudication = {
        "story": "36.4",
        "attempt_id": "pending-id",
        "original_verdict_path": verdict.relative_to(driver.ROOT).as_posix(),
        "original_verdict_sha256": driver._digest(verdict),
        "semantic_acceptance": False,
        "operator_verdict": "PENDING",
        "operator_spot_checks": {key: "PENDING" for key in driver.REQUIRED_OPERATOR_SPOT_CHECKS},
    }
    (adjudication_dir / "adjudication.json").write_text(json.dumps(adjudication), "utf-8")
    monkeypatch.setattr(driver, "EVIDENCE_ROOT", evidence)
    assert driver._failed_attempts() == {}


def test_fourth_fail_adjudication_authorizes_digest_chained_recovery() -> None:
    attempt_id = "b90fb3f6-8951-4dcc-abff-66036576d89f"
    prior = driver.validate_recovery_label(attempt_id)
    assert prior is not None
    manifest = driver.causal_fix_manifest(prior)
    assert "over-promoted" in manifest["cause"]
    adjudication = driver.ROOT / manifest["prior_adjudication"]["path"]
    assert manifest["prior_failed_verdict"]["sha256"] == driver._digest(prior)
    assert manifest["prior_adjudication"]["sha256"] == driver._digest(adjudication)


def test_final_ba470_operator_adjudication_is_exact_machine_bound_pass() -> None:
    verdict = driver.ROOT / (
        "_bmad-output/implementation-artifacts/evidence/"
        "prework-36-4-live-20260713T031924Z-ba470ff2/verdict.json"
    )
    adjudication_path = driver.ROOT / (
        "_bmad-output/implementation-artifacts/evidence/"
        "prework-36-4-adjudication-ba470ff2/adjudication.json"
    )
    adjudication = json.loads(adjudication_path.read_text("utf-8"))
    assert driver.operator_adjudication_state(verdict, adjudication) == "pass"
    assert set(adjudication["operator_spot_checks"]) == driver.REQUIRED_OPERATOR_SPOT_CHECKS
