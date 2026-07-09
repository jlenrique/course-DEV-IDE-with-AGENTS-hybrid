"""Canonical-arc S3 D1/D4 — the gary runner-context parity seam (RED-first #6).

Spec: `_bmad-output/implementation-artifacts/canonical-arc-s3-gary-shadow-parity.md`.

The gary payload branch (`_runner_payload_for_specialist`) supplies, per the
F-802 option-(i) ruling, THREE chartered runner-context keys alongside the
existing ``export_dir``/``gamma_settings``:

- ``cd_styleguide_resolution`` — the committed block verbatim from the
  envelope's LATEST cd contribution (``latest_for_specialist("cd")``, the same
  selector §06 uses), or ``None`` (absent/legacy — never a raise);
- ``directive_digest`` — sha256 of the SAME bytes the gamma-settings parse
  read (read-once, no TOCTOU);
- ``trial_start_directive_digest`` — from ``run_dir/"trial-start.json"``
  (F-801: NOT run.json), ``None`` when the file or key is absent.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from uuid import UUID

import pytest
import yaml

from app.marcus.orchestrator import production_runner
from app.models.runtime.production_envelope import (
    ProductionEnvelope,
    SpecialistContribution,
)

TRIAL_ID = UUID("11111111-2222-4333-8444-555555555555")

EXPECTED_KEYS_WITH_SETTINGS = {
    "export_dir",
    "gamma_settings",
    "cd_styleguide_resolution",
    "directive_digest",
    "trial_start_directive_digest",
}

_BLOCK = {
    "schema_version": 1,
    "status": "resolved",
    "input_picks": None,
    "bound_guides": [{"name": "g", "ssot_digest": "s", "lifecycle": "standard"}],
    "resolved": {"A": {"production_mode": "api", "theme": "t"}},
    "layering_manifest": {
        "base_layer": "styleguide_defaults",
        "composition_rule": "source_derived_wins",
    },
    "resolution_digest": "r" * 64,
    "directive_digest": "d" * 64,
    "default_provenance": None,
    "errors": [],
}


def _gary_payload(
    tmp_path: Path,
    *,
    directive_path: Path | None,
    envelope: ProductionEnvelope | None,
) -> dict:
    payload = production_runner._runner_payload_for_specialist(
        specialist_id="gary",
        directive_path=directive_path,
        bundle_dir=None,
        production_envelope=envelope,
        runs_root=tmp_path,
        trial_id=TRIAL_ID,
    )
    assert payload is not None
    return payload


def _envelope_with_cd(output: dict) -> ProductionEnvelope:
    envelope = ProductionEnvelope(trial_id=TRIAL_ID)
    envelope.add_contribution(
        SpecialistContribution.from_output(
            specialist_id="cd",
            output=output,
            model_used="gpt-5-nano",
            node_id="4.75",
        )
    )
    return envelope


def _seed_directive(tmp_path: Path) -> Path:
    directive = tmp_path / str(TRIAL_ID) / "directive.yaml"
    directive.parent.mkdir(parents=True, exist_ok=True)
    directive.write_text(
        yaml.safe_dump(
            {
                "run_id": str(TRIAL_ID),
                "gamma_settings": [{"variant_id": "A", "styleguide": "g"}],
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    return directive


def test_gary_branch_supplies_full_parity_context(tmp_path: Path) -> None:
    directive = _seed_directive(tmp_path)
    run_dir = tmp_path / str(TRIAL_ID)
    expected_digest = hashlib.sha256(directive.read_bytes()).hexdigest()
    (run_dir / "trial-start.json").write_text(
        json.dumps({"directive_digest": expected_digest, "status": "paused-at-gate"}),
        encoding="utf-8",
    )
    envelope = _envelope_with_cd(
        {"cd_directive": {"experience_profile": "x"}, "styleguide_resolution": _BLOCK}
    )
    payload = _gary_payload(tmp_path, directive_path=directive, envelope=envelope)
    assert set(payload) == EXPECTED_KEYS_WITH_SETTINGS
    # The committed block travels VERBATIM (chartered runner context).
    assert payload["cd_styleguide_resolution"] == _BLOCK
    # Read-once digest of the SAME bytes the settings parse read.
    assert payload["directive_digest"] == expected_digest
    # F-801 non-null witness: sourced from trial-start.json, not run.json.
    assert payload["trial_start_directive_digest"] == expected_digest
    assert payload["gamma_settings"] == [{"variant_id": "A", "styleguide": "g"}]


def test_gary_branch_absent_inputs_yield_honest_nones(tmp_path: Path) -> None:
    payload = _gary_payload(tmp_path, directive_path=None, envelope=None)
    assert payload["cd_styleguide_resolution"] is None
    assert payload["directive_digest"] is None
    assert payload["trial_start_directive_digest"] is None
    assert "gamma_settings" not in payload  # pre-S3 conditional behavior preserved


def test_p4_payload_block_never_aliases_the_live_envelope(tmp_path: Path) -> None:
    # T11 P4(b): the chartered runner-context value is DECOUPLED at capture —
    # mutating the live envelope contribution after payload build must not
    # reach into the payload (the receipt seam is an attestation, not a
    # live pointer into run.json state).
    envelope = _envelope_with_cd(
        {"cd_directive": {"experience_profile": "x"}, "styleguide_resolution": _BLOCK}
    )
    payload = _gary_payload(tmp_path, directive_path=None, envelope=envelope)
    block = payload["cd_styleguide_resolution"]
    assert block == _BLOCK
    live = envelope.latest_for_specialist("cd").output["styleguide_resolution"]
    live["resolved"]["A"]["theme"] = "MUTATED-AFTER-CAPTURE"
    live["bound_guides"][0]["ssot_digest"] = "MUTATED"
    assert block["resolved"]["A"]["theme"] == "t", (
        "payload cd_styleguide_resolution aliases the live envelope contribution"
    )
    assert block["bound_guides"][0]["ssot_digest"] == "s"


def test_gary_branch_legacy_cd_contribution_yields_none_block(tmp_path: Path) -> None:
    # F-802: a cd contribution that PREDATES S1 (no styleguide_resolution key)
    # is legacy — honest None, never a raise.
    envelope = _envelope_with_cd({"cd_directive": {"experience_profile": "x"}})
    payload = _gary_payload(tmp_path, directive_path=None, envelope=envelope)
    assert payload["cd_styleguide_resolution"] is None


def test_gary_branch_malformed_trial_start_is_none_not_a_raise(tmp_path: Path) -> None:
    run_dir = tmp_path / str(TRIAL_ID)
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "trial-start.json").write_text("{not json", encoding="utf-8")
    payload = _gary_payload(tmp_path, directive_path=None, envelope=None)
    assert payload["trial_start_directive_digest"] is None


def test_gary_branch_trial_start_without_digest_key_is_none(tmp_path: Path) -> None:
    run_dir = tmp_path / str(TRIAL_ID)
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "trial-start.json").write_text(
        json.dumps({"status": "cancelled-at-g0"}), encoding="utf-8"
    )
    payload = _gary_payload(tmp_path, directive_path=None, envelope=None)
    assert payload["trial_start_directive_digest"] is None


@pytest.mark.parametrize(
    "bogus_digest",
    [123, "", ["d"], {"nested": "d"}],
    ids=["int", "empty-str", "list", "dict"],
)
def test_p5_non_string_or_empty_trial_start_digest_warns(
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
    bogus_digest: Any,
) -> None:
    # T11 P5: a PRESENT but non-string/empty directive_digest is a
    # producer-side type regression — None is still returned (parity context
    # never blocks dispatch) but the path must be operator-visible (WARN),
    # exactly as the helper's docstring promises.
    import logging

    run_dir = tmp_path / str(TRIAL_ID)
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "trial-start.json").write_text(
        json.dumps({"directive_digest": bogus_digest, "status": "paused-at-gate"}),
        encoding="utf-8",
    )
    with caplog.at_level(logging.WARNING, logger=production_runner.__name__):
        assert production_runner._trial_start_directive_digest(run_dir) is None
    warned = [r for r in caplog.records if "directive_digest" in r.getMessage()]
    assert warned, "a producer-side digest type regression must WARN, never be silent"
    assert all(r.levelno == logging.WARNING for r in warned)


def test_p5_null_digest_stays_silent_legitimate_single_file_shape(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    # `directive_digest: null` is a LEGITIMATE produced shape (single-file
    # trials — the E4 defer note); it must stay silent, not WARN-spam.
    import logging

    run_dir = tmp_path / str(TRIAL_ID)
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "trial-start.json").write_text(
        json.dumps({"directive_digest": None, "status": "registered-offline"}),
        encoding="utf-8",
    )
    with caplog.at_level(logging.WARNING, logger=production_runner.__name__):
        assert production_runner._trial_start_directive_digest(run_dir) is None
    assert caplog.records == []


def test_p5_non_mapping_trial_start_payload_warns(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    # A parseable-but-non-mapping trial-start.json is malformed content — the
    # docstring promises a WARN for that class too.
    import logging

    run_dir = tmp_path / str(TRIAL_ID)
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "trial-start.json").write_text("[1, 2, 3]", encoding="utf-8")
    with caplog.at_level(logging.WARNING, logger=production_runner.__name__):
        assert production_runner._trial_start_directive_digest(run_dir) is None
    assert any("trial-start.json" in r.getMessage() for r in caplog.records)


def test_gamma_settings_wrapper_behavior_unchanged(tmp_path: Path) -> None:
    # D4 read-once refactor: `_gamma_settings_from_directive` keeps its exact
    # public behavior (None cases included) as a thin wrapper.
    assert production_runner._gamma_settings_from_directive(None) is None
    missing = tmp_path / "nope.yaml"
    assert production_runner._gamma_settings_from_directive(missing) is None
    directive = _seed_directive(tmp_path)
    assert production_runner._gamma_settings_from_directive(directive) == [
        {"variant_id": "A", "styleguide": "g"}
    ]


def test_real_start_trial_write_feeds_the_seam_reader(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """T11 P1: producer-side attestation witness — the REAL `start_trial`
    write of ``trial-start.json`` (trial.py:536) is what
    ``_trial_start_directive_digest`` reads. A producer-side key rename or
    digest-shape change must go RED here (closes the last silent-degrade seam
    on F-703 — the walk-level witnesses fabricate the file; this one does not).

    The LLM-driven composer and the walk are stubbed at their established
    seams (the S2 preflight-test pattern); the WRITE under test — result dict
    -> trial-start.json — runs the real production code end to end.
    """
    import app.marcus.cli.trial as trial_module
    from app.marcus.cli.trial import start_trial

    def _compose(
        *,
        corpus_dir: Path,
        run_dir: Path,
        run_id: Any,
        llm: Any = None,
        gamma_settings: Any = None,
    ) -> tuple[Path, str]:
        del llm, gamma_settings
        run_dir.mkdir(parents=True, exist_ok=True)
        path = run_dir / "directive.yaml"
        path.write_text(
            yaml.safe_dump(
                {
                    "run_id": str(run_id),
                    "corpus_dir": corpus_dir.as_posix(),
                    "sources": [],
                },
                sort_keys=False,
            ),
            encoding="utf-8",
        )
        return path, hashlib.sha256(path.read_bytes()).hexdigest()

    monkeypatch.setattr(trial_module, "compose_and_write", _compose)
    monkeypatch.setattr(
        trial_module,
        "run_production_trial",
        lambda **_k: SimpleNamespace(
            status="paused-at-gate",
            paused_gate="G1",
            paused_error_tag=None,
            cost_report_path=None,
            production_clone_launch_evidence=False,
        ),
    )
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    (corpus / "intro.md").write_text("body", encoding="utf-8")
    runs_root = tmp_path / "runs"

    result = start_trial(
        preset="production",
        input_path=corpus,
        operator_id="operator_test",
        trial_id=TRIAL_ID,
        allow_offline_cost_report=True,
        runs_root=runs_root,
        auto_confirm_directive=True,
    )

    run_dir = runs_root / str(TRIAL_ID)
    directive = run_dir / "directive.yaml"
    expected_digest = hashlib.sha256(directive.read_bytes()).hexdigest()
    # The producer attested the post-confirm directive bytes (trial.py:470).
    assert result["directive_digest"] == expected_digest
    assert (run_dir / "trial-start.json").is_file(), "start_trial must persist the attestation"
    # THE seam: the consumer reads exactly what the REAL producer wrote.
    assert production_runner._trial_start_directive_digest(run_dir) == expected_digest


def test_seam_docstring_enumerates_the_parity_context(tmp_path: Path) -> None:
    del tmp_path
    # F-203 precedent: the seam docstring's runner-context enumeration names
    # the S3 keys (chartered runner context, not content delivery).
    doc = production_runner._runner_payload_for_specialist.__doc__ or ""
    for key in (
        "cd_styleguide_resolution",
        "directive_digest",
        "trial_start_directive_digest",
    ):
        assert key in doc, f"seam docstring does not charter {key!r}"
