"""Canonical-arc S3 D3 — Gary's shadow-parity audit at the resolve site.

Spec: `_bmad-output/implementation-artifacts/canonical-arc-s3-gary-shadow-parity.md`
(RED-first plan #2: ``test_receipt_rides_contribution`` + AC-4
``test_dispatch_bytes_identical_with_audit``; AC-1 non-vacuity trio; AC-2
status-keying at the gary level).

CD's block is built through the REAL committed emission
(`_styleguide_resolution_from_projection`) — test-level cross-imports are the
chartered meeting point (F-403 lockstep precedent); production import coupling
between the modules stays forbidden.

The audit is observability-ONLY: dispatched packets byte-identical (AC-4,
protected source-detail→Gamma conveyance), WARN-seed branch untouched, the
comparator never raises and never alters dispatch.
"""

from __future__ import annotations

import inspect
import json
import logging
import zipfile
from pathlib import Path
from typing import Any

import pytest
import yaml

from app.specialists.cd.graph import _styleguide_resolution_from_projection
from app.specialists.gary import _act as gary_act
from app.styleguide.parity import canonical_resolution_digest
from app.styleguide.resolver import (
    GAMMA_STYLE_GUIDES_PATH,
    load_style_guides,
    resolve_styleguide,
)

GARY_LOGGER = "app.specialists.gary._act"
REAL_GUIDE = "hil-2026-apc-crossroads-classic"
SAME_DIGEST = "f" * 64


class _CapturingClient:
    """Offline Gamma client: captures generate_deck kwargs; no network."""

    def __init__(self) -> None:
        self.generate_calls: list[dict[str, object]] = []

    def list_themes(self, limit: int = 20) -> list[dict[str, str]]:
        del limit
        return [
            {"id": "njim9kuhfnljvaa", "name": "2026 HIL APC Tejal"},
            {"id": "t-parity", "name": "Parity Theme"},
        ]

    def generate_deck(self, input_text: str, **kwargs: object) -> dict[str, object]:
        self.generate_calls.append({"input_text": input_text, **kwargs})
        return {
            "generation_id": f"gen-{len(self.generate_calls)}",
            "exportUrl": "https://example.invalid/export.zip",
        }


def _titled_zip(tmp_path: Path) -> Path:
    tmp_path.mkdir(parents=True, exist_ok=True)
    zpath = tmp_path / "gamma-export.zip"
    with zipfile.ZipFile(zpath, "w") as archive:
        archive.writestr("1_Only-Slide.png", b"bytes::only-slide")
    return zpath


def _run(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    payload_extra: dict[str, Any],
    *,
    gamma_settings: list[dict[str, Any]] | None = None,
) -> tuple[dict[str, Any], _CapturingClient]:
    zpath = _titled_zip(tmp_path)
    monkeypatch.setattr(
        gary_act, "download_export", lambda url, *, output_dir, filename: str(zpath)
    )
    client = _CapturingClient()
    payload: dict[str, Any] = {
        "slides": [{"slide_id": "s1", "title": "Only Slide"}],
        "export_dir": str(tmp_path / "exports"),
        **payload_extra,
    }
    if gamma_settings is not None:
        payload["gamma_settings"] = gamma_settings
    result = gary_act.generate_gamma_variants(payload, client=client)
    return result, client


def _real_ssot_cd_block(
    picks: list[dict[str, Any]] | None, *, directive_digest: str = SAME_DIGEST
) -> dict[str, Any]:
    """CD's committed emission over the REAL SSOT (deterministic neck)."""
    return _styleguide_resolution_from_projection(
        {"gamma_settings": picks, "directive_digest": directive_digest}
    )


def _parity_records(caplog: pytest.LogCaptureFixture) -> list[logging.LogRecord]:
    return [r for r in caplog.records if "styleguide parity" in r.getMessage()]


# --- RED-2: the receipt rides the contribution output --------------------------


def test_receipt_rides_contribution(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    block = _real_ssot_cd_block([{"variant_id": "A", "styleguide": REAL_GUIDE}])
    result, _client = _run(
        tmp_path,
        monkeypatch,
        {
            "cd_styleguide_resolution": block,
            "directive_digest": SAME_DIGEST,
            "trial_start_directive_digest": SAME_DIGEST,
        },
        gamma_settings=[{"variant_id": "A", "styleguide": REAL_GUIDE}],
    )
    receipt = result["styleguide_parity"]
    assert receipt["schema_version"] == 1
    assert receipt["outcome"] == "ok"
    assert receipt["reason"] == "match"
    assert receipt["clock_eligible"] is True
    assert receipt["gary_resolution_digest"] == block["resolution_digest"]


def test_receipt_lands_in_act_output_as_sibling_key(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Through the graph ``_act`` slides path: the receipt is a sibling key in
    the contribution output blob (provenance in the carrier — no shadow store)."""
    from app.models.state.cache_state import CacheState
    from app.models.state.model_resolution_entry import ModelResolutionEntry
    from app.models.state.run_state import RunState
    from app.specialists.gary.graph import _act as gary_graph_act

    zpath = _titled_zip(tmp_path)
    monkeypatch.setattr(
        gary_act, "download_export", lambda url, *, output_dir, filename: str(zpath)
    )
    monkeypatch.setattr(gary_act, "GammaClient", _CapturingClient)
    payload = {
        "slides": [{"slide_id": "s1", "title": "Only Slide"}],
        "export_dir": str(tmp_path / "exports"),
        "gamma_settings": [{"variant_id": "A", "styleguide": REAL_GUIDE}],
        "cd_styleguide_resolution": _real_ssot_cd_block(
            [{"variant_id": "A", "styleguide": REAL_GUIDE}]
        ),
        "directive_digest": SAME_DIGEST,
        "trial_start_directive_digest": SAME_DIGEST,
    }
    state = RunState(
        graph_version="v0.1-stub",
        temperature=0.0,
        model_resolution_trail=[
            ModelResolutionEntry(
                level="per_specialist",
                requested="gpt-5-nano",
                resolved="gpt-5-nano",
                reason="test",
                timestamp="2026-01-01T00:00:00Z",
                cache_prefix_hash="a" * 64,
            )
        ],
        cache_state=CacheState(
            cache_prefix=json.dumps(
                payload, sort_keys=True, ensure_ascii=True, separators=(",", ":")
            ),
            entries_count=0,
        ),
    )
    update = gary_graph_act(state)
    output = json.loads(update["cache_state"]["cache_prefix"])
    assert output["styleguide_parity"]["outcome"] == "ok"
    assert output["styleguide_parity"]["reason"] == "match"
    # Sibling key: the load-bearing slide output is untouched beside it.
    assert output["gary_slide_output"]


# --- AC-1 trio: three fixtures, three DISTINCT outcomes -------------------------


def _write_ssot(path: Path, *, tone: str) -> Path:
    path.write_text(
        yaml.safe_dump(
            {
                "style_guides": {
                    "parity-probe-guide": {
                        "production_mode": "api",
                        "theme": {"id": "t-parity"},
                        "prompt_configuration": {"text_content": {"tone": tone}},
                    }
                }
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    return path


def test_ac1_divergence_must_warn(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    # Same directive bytes (digests EQUAL) but the SSOT content differs
    # between CD's resolution and Gary's read (ssot_path injection on the CD
    # side; Gary's module-level SSOT path redirected to the mutated copy).
    cd_ssot = _write_ssot(tmp_path / "ssot-cd.yaml", tone="calm")
    gary_ssot = _write_ssot(tmp_path / "ssot-gary.yaml", tone="urgent")
    block = _styleguide_resolution_from_projection(
        {
            "gamma_settings": [{"variant_id": "A", "styleguide": "parity-probe-guide"}],
            "directive_digest": SAME_DIGEST,
        },
        ssot_path=cd_ssot,
    )
    assert block["status"] == "resolved"
    monkeypatch.setattr(gary_act, "GAMMA_STYLE_GUIDES_PATH", gary_ssot)
    with caplog.at_level(logging.INFO, logger=GARY_LOGGER):
        result, _client = _run(
            tmp_path,
            monkeypatch,
            {
                "cd_styleguide_resolution": block,
                "directive_digest": SAME_DIGEST,
                "trial_start_directive_digest": SAME_DIGEST,
            },
            gamma_settings=[{"variant_id": "A", "styleguide": "parity-probe-guide"}],
        )
    receipt = result["styleguide_parity"]
    assert receipt["outcome"] == "divergence"
    assert receipt["reason"] == "resolution-mismatch"
    # Both envelopes ride the receipt (§7 WARN-receipt contract).
    assert receipt["detail"]["cd_block"] == block
    assert receipt["detail"]["gary_view"]["picks"] == {"A": "parity-probe-guide"}
    warn_records = [r for r in _parity_records(caplog) if r.levelno == logging.WARNING]
    assert warn_records, "divergence MUST emit a WARN log record"
    # Distinct message from the :523 WARN-seed.
    assert all("DEFAULT_VARIANT_PAIR" not in r.getMessage() for r in warn_records)


def test_ac1_match_is_silent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    block = _real_ssot_cd_block([{"variant_id": "A", "styleguide": REAL_GUIDE}])
    with caplog.at_level(logging.DEBUG, logger=GARY_LOGGER):
        result, _client = _run(
            tmp_path,
            monkeypatch,
            {
                "cd_styleguide_resolution": block,
                "directive_digest": SAME_DIGEST,
                "trial_start_directive_digest": SAME_DIGEST,
            },
            gamma_settings=[{"variant_id": "A", "styleguide": REAL_GUIDE}],
        )
    receipt = result["styleguide_parity"]
    assert receipt["outcome"] == "ok"
    assert receipt["reason"] == "match"
    assert receipt["clock_eligible"] is True
    assert _parity_records(caplog) == [], "match must be SILENT (receipt data only)"


def test_ac1_ordering_gap_is_info_not_warn(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    # CD authored before the pick landed (legacy/G2B-era flow): CD saw no
    # picks; Gary's payload carries one.
    block = _real_ssot_cd_block(None)
    assert block["status"] == "no_picks_at_authoring"
    with caplog.at_level(logging.INFO, logger=GARY_LOGGER):
        result, _client = _run(
            tmp_path,
            monkeypatch,
            {
                "cd_styleguide_resolution": block,
                "directive_digest": SAME_DIGEST,
                "trial_start_directive_digest": SAME_DIGEST,
            },
            gamma_settings=[{"variant_id": "A", "styleguide": REAL_GUIDE}],
        )
    receipt = result["styleguide_parity"]
    assert receipt["outcome"] == "expected-ordering-gap"
    assert receipt["reason"] == "cd-saw-no-picks"
    records = _parity_records(caplog)
    assert records, "ordering gap must emit an INFO record"
    assert all(r.levelno == logging.INFO for r in records), "never cry-wolf WARN"


# --- AC-2: F-702 status-keying at the gary level ---------------------------------


def test_ac2_both_pickless_is_status_keyed_and_seed_never_compared(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    block = _real_ssot_cd_block(None)
    with caplog.at_level(logging.DEBUG, logger=GARY_LOGGER):
        result, _client = _run(
            tmp_path,
            monkeypatch,
            {
                "cd_styleguide_resolution": block,
                "directive_digest": SAME_DIGEST,
                "trial_start_directive_digest": SAME_DIGEST,
            },
            gamma_settings=[{"variant_id": "A"}],  # present variant, no pick
        )
    receipt = result["styleguide_parity"]
    assert receipt["outcome"] == "ok"
    assert receipt["reason"] == "status-keyed-no-picks"
    assert receipt["clock_eligible"] is False
    # F-804: Gary's DEFAULT_VARIANT_PAIR seed was NOT compared against CD's
    # default-A resolution — the compared gary surface is EMPTY even though
    # CD's block carries the F-202 default binding.
    assert receipt["gary_resolution_digest"] == canonical_resolution_digest({})
    assert receipt["gary_bound_guides"] == []
    assert block["resolved"], "CD's default-A binding exists and was NOT compared"
    # The honesty WARN-seed (:518-528) still fired — behavior untouched (AC-4).
    seed_records = [
        r for r in caplog.records if "DEFAULT_VARIANT_PAIR" in r.getMessage()
    ]
    assert seed_records and all(r.levelno == logging.WARNING for r in seed_records)
    # No parity WARN/INFO — the ok case is silent.
    assert _parity_records(caplog) == []


# --- AC-3 (gary-level drift leg) --------------------------------------------------


def test_ac3_directive_drift_never_diverges_at_gary(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # CD resolved a DIFFERENT guide from OLDER directive bytes; Gary's read
    # came from newer bytes (digest mismatch) — INFO family, never WARN.
    block = _real_ssot_cd_block(
        [{"variant_id": "A", "styleguide": "videographic-glance-track"}],
        directive_digest="0" * 64,
    )
    result, _client = _run(
        tmp_path,
        monkeypatch,
        {
            "cd_styleguide_resolution": block,
            "directive_digest": SAME_DIGEST,
            "trial_start_directive_digest": SAME_DIGEST,
        },
        gamma_settings=[{"variant_id": "A", "styleguide": REAL_GUIDE}],
    )
    receipt = result["styleguide_parity"]
    assert receipt["outcome"] == "expected-ordering-gap"
    assert receipt["reason"] == "directive-drift"
    assert receipt["cd_directive_digest"] == "0" * 64
    assert receipt["gary_directive_digest"] == SAME_DIGEST


# --- T11 P3: the gap INFO log is reason-keyed (no "legacy" editorializing on
# --- drift/schema-newer — a mid-walk directive mutation is triage-worthy) ----------


def test_p3_drift_gap_log_is_reason_keyed_not_legacy_editorialized(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    block = _real_ssot_cd_block(
        [{"variant_id": "A", "styleguide": REAL_GUIDE}], directive_digest="0" * 64
    )
    with caplog.at_level(logging.INFO, logger=GARY_LOGGER):
        result, _client = _run(
            tmp_path,
            monkeypatch,
            {
                "cd_styleguide_resolution": block,
                "directive_digest": SAME_DIGEST,
                "trial_start_directive_digest": SAME_DIGEST,
            },
            gamma_settings=[{"variant_id": "A", "styleguide": REAL_GUIDE}],
        )
    assert result["styleguide_parity"]["reason"] == "directive-drift"
    records = _parity_records(caplog)
    assert records and all(r.levelno == logging.INFO for r in records)
    message = "\n".join(r.getMessage() for r in records)
    assert "directive-drift" in message, "the INFO must name the reason"
    assert "mutated" in message, "drift is a mid-walk directive mutation — say so"
    # A mid-walk mutation is triage-worthy, NOT an expected legacy state.
    assert "legacy" not in message.lower()
    assert "pre-S2" not in message


def test_p3_schema_newer_gap_log_never_says_legacy(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    block = dict(
        _real_ssot_cd_block([{"variant_id": "A", "styleguide": REAL_GUIDE}]),
        schema_version=2,
    )
    with caplog.at_level(logging.INFO, logger=GARY_LOGGER):
        result, _client = _run(
            tmp_path,
            monkeypatch,
            {
                "cd_styleguide_resolution": block,
                "directive_digest": SAME_DIGEST,
                "trial_start_directive_digest": SAME_DIGEST,
            },
            gamma_settings=[{"variant_id": "A", "styleguide": REAL_GUIDE}],
        )
    assert result["styleguide_parity"]["reason"] == "cd-schema-newer"
    records = _parity_records(caplog)
    assert records and all(r.levelno == logging.INFO for r in records)
    message = "\n".join(r.getMessage() for r in records)
    assert "cd-schema-newer" in message
    assert "legacy" not in message.lower()
    assert "pre-S2" not in message


# --- AC-6 (gary-level legacy tolerance) -------------------------------------------


def test_ac6_absent_cd_context_dispatches_clean_with_honest_receipt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # No parity context at all (legacy harness payload): dispatch is CLEAN,
    # receipt is honest — never a raise (F-802 tolerance at the act level).
    result, client = _run(
        tmp_path,
        monkeypatch,
        {},
        gamma_settings=[{"variant_id": "A", "styleguide": REAL_GUIDE}],
    )
    receipt = result["styleguide_parity"]
    assert receipt["outcome"] == "expected-ordering-gap"
    assert receipt["reason"] == "cd-envelope-absent-legacy"
    assert client.generate_calls, "dispatch proceeded untouched"


# --- AC-4: observability-only (protected invariant) --------------------------------


def _canon(value: Any) -> str:
    # T11 P6: STRICT canonicalization — no `default=` escape hatch, so a
    # type-differing packet (e.g. Path vs str) raises instead of silently
    # canonicalizing equal (soft teeth on the AC-4 byte-identity pin).
    return json.dumps(value, sort_keys=True, ensure_ascii=True)


def test_p6_canonicalizer_has_type_teeth() -> None:
    """T11 P6 probe: the OLD `default=str` canonicalizer MASKED type
    differences — a Path-typed leaf canonicalized equal to its str twin, so a
    type-differing dispatched packet could pass the AC-4 byte-identity pin.
    The tightened `_canon` refuses to canonicalize such a packet silently."""
    old_style = lambda v: json.dumps(  # noqa: E731 — the defect under probe
        v, sort_keys=True, ensure_ascii=True, default=str
    )
    typed = {"export_path": Path("exports/a"), "num_cards": 1}
    stringly = {"export_path": str(Path("exports/a")), "num_cards": 1}
    assert old_style(typed) == old_style(stringly), (
        "probe: default=str masks Path-vs-str packet differences"
    )
    with pytest.raises(TypeError):
        _canon(typed)


def test_dispatch_bytes_identical_with_audit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """RED-by-construction (AC-4): the dispatched Gamma packet and the merged
    per-variant settings are byte-identical WITH and WITHOUT the parity
    context present in the payload — the audit is observability-only."""
    settings = [
        {
            "variant_id": "A",
            "styleguide": REAL_GUIDE,
            "keywords": ["hero-diagram", "clinical-navy-gold"],
        }
    ]
    result_plain, client_plain = _run(
        tmp_path / "plain", monkeypatch, {}, gamma_settings=settings
    )
    block = _real_ssot_cd_block([{"variant_id": "A", "styleguide": REAL_GUIDE}])
    result_audited, client_audited = _run(
        tmp_path / "audited",
        monkeypatch,
        {
            "cd_styleguide_resolution": block,
            "directive_digest": SAME_DIGEST,
            "trial_start_directive_digest": SAME_DIGEST,
        },
        gamma_settings=settings,
    )
    # T11 P6: non-vacuity — the byte-identity claim is about REAL dispatches,
    # so the compared call lists must not be trivially empty.
    assert client_plain.generate_calls, "plain run dispatched nothing — vacuous pin"
    assert client_audited.generate_calls, "audited run dispatched nothing — vacuous pin"
    assert _canon(client_plain.generate_calls) == _canon(client_audited.generate_calls)
    assert _canon(result_plain["variant_gamma_settings"]) == _canon(
        result_audited["variant_gamma_settings"]
    )
    # Non-vacuity: the audited run really carried a receipt.
    assert result_audited["styleguide_parity"]["outcome"] == "ok"


def test_resolve_with_guides_byte_identical_to_path_read() -> None:
    # AC-4: ``resolve_styleguide(name, guides=...)`` over the ONCE-read SSOT
    # bytes is byte-identical to the per-call path-reading resolve.
    ssot_bytes = GAMMA_STYLE_GUIDES_PATH.read_bytes()
    guides = load_style_guides(GAMMA_STYLE_GUIDES_PATH, content=ssot_bytes).get(
        "style_guides", {}
    )
    for name in (REAL_GUIDE, "videographic-glance-track"):
        assert _canon(resolve_styleguide(name, guides=guides)) == _canon(
            resolve_styleguide(name)
        )


def test_warn_seed_branch_text_byte_untouched() -> None:
    # AC-4 fence: the styleguide-less honesty WARN-seed (:518-528) is
    # byte-untouched — S4 owns the flip (F-705).
    source = inspect.getsource(gary_act._normalized_gamma_settings)
    assert (
        '"variant %s present with no bound styleguide; seeding from "\n'
        '                "DEFAULT_VARIANT_PAIR base — fail-loud deferred to cd-envelope-authoring"'
        in source
    )
    assert "merged = dict(by_variant[variant_id])" in source


def test_p4_receipt_survives_post_run_mutation_of_sources_and_settings(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # T11 P4: the persisted-able receipt is DECOUPLED — mutating the payload's
    # cd block and the returned merged settings AFTER the run leaves the
    # receipt byte-unchanged, and the receipt json.dumps cleanly (envelope
    # persistence survives ANY input).
    cd_ssot = _write_ssot(tmp_path / "ssot-cd.yaml", tone="calm")
    gary_ssot = _write_ssot(tmp_path / "ssot-gary.yaml", tone="urgent")
    block = _styleguide_resolution_from_projection(
        {
            "gamma_settings": [{"variant_id": "A", "styleguide": "parity-probe-guide"}],
            "directive_digest": SAME_DIGEST,
        },
        ssot_path=cd_ssot,
    )
    monkeypatch.setattr(gary_act, "GAMMA_STYLE_GUIDES_PATH", gary_ssot)
    result, _client = _run(
        tmp_path,
        monkeypatch,
        {
            "cd_styleguide_resolution": block,
            "directive_digest": SAME_DIGEST,
            "trial_start_directive_digest": SAME_DIGEST,
        },
        gamma_settings=[{"variant_id": "A", "styleguide": "parity-probe-guide"}],
    )
    receipt = result["styleguide_parity"]
    assert receipt["outcome"] == "divergence"  # detail carries both envelopes
    snapshot = json.dumps(receipt, sort_keys=True)  # also: must not raise
    # Mutate every source object the receipt could have aliased.
    block["resolved"]["A"]["production_mode"] = "MUTATED-AFTER-RUN"
    block["bound_guides"][0]["ssot_digest"] = "MUTATED"
    for entry in result["variant_gamma_settings"]:
        entry["additional_instructions"] = "MUTATED-AFTER-RUN"
    assert json.dumps(receipt, sort_keys=True) == snapshot, (
        "post-run mutation of source objects leaked into the parity receipt"
    )


def test_comparator_failure_never_blocks_dispatch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # A garbage CD block (non-dict) must never raise or alter dispatch.
    result, client = _run(
        tmp_path,
        monkeypatch,
        {"cd_styleguide_resolution": ["not", "a", "block"]},
        gamma_settings=[{"variant_id": "A", "styleguide": REAL_GUIDE}],
    )
    assert result["styleguide_parity"]["outcome"] == "divergence"
    assert result["styleguide_parity"]["reason"] == "contract-violation"
    assert client.generate_calls
