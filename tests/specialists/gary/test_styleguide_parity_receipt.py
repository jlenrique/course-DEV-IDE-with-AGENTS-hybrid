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


def test_ac1_divergence_receipt_logs_error_and_caller_halts(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    # Canonical-arc S4 amendment (AC-9 extend, not weaken): S3 asserted the
    # divergence WARN-and-PROCEED; S4 flips it. The HELPER still returns a
    # receipt carrying BOTH envelopes and NEVER raises (comparator + helper
    # unchanged); the divergence log is now an ERROR; the CALLER
    # (generate_gamma_variants) halts pre-spend.
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
    # Helper level: the receipt still classifies divergence and carries BOTH
    # envelopes; the helper never raises.
    resolve_view: dict[str, Any] = {}
    gary_act._normalized_gamma_settings(
        {
            "gamma_settings": [
                {"variant_id": "A", "styleguide": "parity-probe-guide"}
            ],
            "directive_digest": SAME_DIGEST,
            "trial_start_directive_digest": SAME_DIGEST,
        },
        resolve_view=resolve_view,
    )
    with caplog.at_level(logging.INFO, logger=GARY_LOGGER):
        receipt = gary_act._styleguide_parity_receipt(
            {
                "cd_styleguide_resolution": block,
                "directive_digest": SAME_DIGEST,
                "trial_start_directive_digest": SAME_DIGEST,
            },
            resolve_view,
        )
    assert receipt["outcome"] == "divergence"
    assert receipt["reason"] == "resolution-mismatch"
    # Both envelopes ride the receipt (§7 receipt contract).
    assert receipt["detail"]["cd_block"] == block
    assert receipt["detail"]["gary_view"]["picks"] == {"A": "parity-probe-guide"}
    error_records = [r for r in _parity_records(caplog) if r.levelno == logging.ERROR]
    assert error_records, "divergence MUST emit an ERROR log record (S4 flip)"
    # Distinct message from the styleguide-less honesty seed.
    assert all("DEFAULT_VARIANT_PAIR" not in r.getMessage() for r in error_records)
    # Caller flip: generate_gamma_variants halts pre-spend on the divergence.
    with pytest.raises(gary_act.GaryActError) as excinfo:
        _run(
            tmp_path,
            monkeypatch,
            {
                "cd_styleguide_resolution": block,
                "directive_digest": SAME_DIGEST,
                "trial_start_directive_digest": SAME_DIGEST,
            },
            gamma_settings=[{"variant_id": "A", "styleguide": "parity-probe-guide"}],
        )
    assert excinfo.value.tag == "gamma.styleguide.parity-divergence"


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


def test_present_pickless_variant_now_raises_unbound(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Canonical-arc S4 amendment (AC-9 extend, not weaken): S3 exercised a
    # PRESENT variant with no pick reaching the parity status-keying
    # (ok/status-keyed-no-picks, proceed). S4 Flip A makes that same
    # styleguide-less named variant a governance error — it now raises
    # gamma.styleguide.unbound BEFORE the parity receipt is even computed. The
    # parity status-keying itself is still witnessed at the comparator level
    # (tests/styleguide/test_parity_comparator.py) and via the empty-settings
    # default-A path (test_styleguide_parity_error_flip.py AC-5).
    with pytest.raises(gary_act.GaryActError) as excinfo:
        _run(
            tmp_path,
            monkeypatch,
            {
                "cd_styleguide_resolution": _real_ssot_cd_block(None),
                "directive_digest": SAME_DIGEST,
                "trial_start_directive_digest": SAME_DIGEST,
            },
            gamma_settings=[{"variant_id": "A"}],  # present variant, no pick
        )
    assert excinfo.value.tag == "gamma.styleguide.unbound"


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


def test_warn_seed_branch_flipped_to_raise() -> None:
    # Canonical-arc S4 amendment (AC-9 extend, not weaken): S3 fenced the
    # styleguide-less honesty WARN-seed as byte-untouched ("S4 owns the flip",
    # F-705). S4 now OWNS it — the WARN-seed is retired and the branch raises
    # the governance error.
    source = inspect.getsource(gary_act._normalized_gamma_settings)
    assert "fail-loud deferred to cd-envelope-authoring" not in source
    assert "merged = dict(by_variant[variant_id])" not in source
    assert 'tag="gamma.styleguide.unbound"' in source


def test_p4_receipt_survives_post_run_mutation_of_sources_and_settings(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # T11 P4: the persisted-able receipt is DECOUPLED — mutating the payload's
    # cd block and the returned merged settings AFTER the run leaves the
    # receipt byte-unchanged, and the receipt json.dumps cleanly (envelope
    # persistence survives ANY input).
    # Canonical-arc S4 amendment (AC-9): the CALLER now halts on divergence, so
    # the P4 receipt-decoupling witness runs at the HELPER level (which still
    # returns the receipt and never raises).
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
    resolve_view: dict[str, Any] = {}
    settings = gary_act._normalized_gamma_settings(
        {
            "gamma_settings": [
                {"variant_id": "A", "styleguide": "parity-probe-guide"}
            ],
            "directive_digest": SAME_DIGEST,
            "trial_start_directive_digest": SAME_DIGEST,
        },
        resolve_view=resolve_view,
    )
    receipt = gary_act._styleguide_parity_receipt(
        {
            "cd_styleguide_resolution": block,
            "directive_digest": SAME_DIGEST,
            "trial_start_directive_digest": SAME_DIGEST,
        },
        resolve_view,
    )
    assert receipt["outcome"] == "divergence"  # detail carries both envelopes
    snapshot = json.dumps(receipt, sort_keys=True)  # also: must not raise
    # Mutate every source object the receipt could have aliased.
    block["resolved"]["A"]["production_mode"] = "MUTATED-AFTER-RUN"
    block["bound_guides"][0]["ssot_digest"] = "MUTATED"
    for entry in settings:
        entry["additional_instructions"] = "MUTATED-AFTER-RUN"
    assert json.dumps(receipt, sort_keys=True) == snapshot, (
        "post-run mutation of source objects leaked into the parity receipt"
    )


def test_comparator_contract_violation_now_halts_dispatch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Canonical-arc S4 amendment (AC-9 extend, not weaken + F-1102): S3 let a
    # garbage CD block (divergence/contract-violation) PROCEED (observability-
    # only). S4 Flip B halts pre-spend on ANY divergence — including the
    # comparator's contract-violation fallback (a broken/garbage envelope
    # SURFACES instead of shipping on unverified parity).
    with pytest.raises(gary_act.GaryActError) as excinfo:
        _run(
            tmp_path,
            monkeypatch,
            {"cd_styleguide_resolution": ["not", "a", "block"]},
            gamma_settings=[{"variant_id": "A", "styleguide": REAL_GUIDE}],
        )
    assert excinfo.value.tag == "gamma.styleguide.parity-divergence"
    assert "contract-violation" in str(excinfo.value)
