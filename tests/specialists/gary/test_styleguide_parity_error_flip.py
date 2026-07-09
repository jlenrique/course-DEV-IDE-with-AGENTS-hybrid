"""Canonical-arc S4 — Flip B: parity `divergence` -> pre-spend hard failure.

Spec: `_bmad-output/implementation-artifacts/canonical-arc-s4-fail-loud-flip.md`
(D2/D3; RED-first plan #2 + #5). Covers AC-4 (Flip B raises
`gamma.styleguide.parity-divergence` pre-dispatch, parametrized over all THREE
divergence reasons INCLUDING the total-comparator crash fallback F-1102,
message carries the reason, deterministic-not-retryable) and AC-5 (every
tolerated state — ok/*, all four expected-ordering-gap reasons, and a
legacy/absent CD block — proceeds without a raise; anti-over-fire pin).

`app/styleguide/parity.py` is FROZEN. Flip B lives in `generate_gamma_variants`
immediately after the `_styleguide_parity_receipt(...)` call and BEFORE the
variants dispatch loop — a raise on the `divergence` outcome only.
"""

from __future__ import annotations

import zipfile
from pathlib import Path
from typing import Any

import pytest
import yaml

from app.marcus.orchestrator.production_runner import _RETRYABLE_DISPATCH_TAGS
from app.specialists.cd.graph import _styleguide_resolution_from_projection
from app.specialists.gary import _act as gary_act

REAL_GUIDE = "hil-2026-apc-crossroads-classic"
SAME_DIGEST = "f" * 64
UNBOUND_TAG = "gamma.styleguide.unbound"
DIVERGENCE_TAG = "gamma.styleguide.parity-divergence"


class _CapturingClient:
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
    return _styleguide_resolution_from_projection(
        {"gamma_settings": picks, "directive_digest": directive_digest}
    )


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


# --- D3: the new tags are deterministic error-pauses, never retryable -----------


def test_d3_new_tags_are_not_retryable() -> None:
    assert UNBOUND_TAG not in _RETRYABLE_DISPATCH_TAGS
    assert DIVERGENCE_TAG not in _RETRYABLE_DISPATCH_TAGS


# --- AC-4: Flip B raises pre-dispatch on every divergence reason -----------------


def _force_resolution_mismatch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> tuple[dict[str, Any], _CapturingClient]:
    # Same directive bytes (digests EQUAL), but the SSOT content differs between
    # CD's resolution and Gary's read -> divergence/resolution-mismatch.
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
    return _run(
        tmp_path,
        monkeypatch,
        {
            "cd_styleguide_resolution": block,
            "directive_digest": SAME_DIGEST,
            "trial_start_directive_digest": SAME_DIGEST,
        },
        gamma_settings=[{"variant_id": "A", "styleguide": "parity-probe-guide"}],
    )


def _force_cd_unresolvable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> tuple[dict[str, Any], _CapturingClient]:
    # A full v1 block whose status is unresolvable_pick on the SAME directive
    # bytes, while Gary resolves cleanly -> divergence/cd-unresolvable-but-gary-resolved.
    block = dict(
        _real_ssot_cd_block([{"variant_id": "A", "styleguide": REAL_GUIDE}]),
        status="unresolvable_pick",
    )
    return _run(
        tmp_path,
        monkeypatch,
        {
            "cd_styleguide_resolution": block,
            "directive_digest": SAME_DIGEST,
            "trial_start_directive_digest": SAME_DIGEST,
        },
        gamma_settings=[{"variant_id": "A", "styleguide": REAL_GUIDE}],
    )


def _force_contract_violation_garbage(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> tuple[dict[str, Any], _CapturingClient]:
    # A non-dict CD block -> divergence/contract-violation.
    return _run(
        tmp_path,
        monkeypatch,
        {"cd_styleguide_resolution": ["not", "a", "block"]},
        gamma_settings=[{"variant_id": "A", "styleguide": REAL_GUIDE}],
    )


def _force_comparator_crash(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> tuple[dict[str, Any], _CapturingClient]:
    # F-1102: drive the TOTAL comparator to its crash-path fallback by seeding
    # an UNSERIALIZABLE value into Gary's resolved_base, so the comparator's
    # canonical_resolution_digest(json.dumps) raises internally and folds to
    # divergence/contract-violation. Post-flip this MUST halt (halt-on-auditor-
    # self-crash is the INTENDED fail-loud posture).
    real_resolve = gary_act.resolve_styleguide

    def _poison(name: str, *, guides: Any = None) -> dict[str, Any]:
        base = dict(real_resolve(name, guides=guides))
        base["__unserializable__"] = {1, 2, 3}  # a set -> json.dumps TypeError
        return base

    monkeypatch.setattr(gary_act, "resolve_styleguide", _poison)
    return _run(
        tmp_path,
        monkeypatch,
        {
            "cd_styleguide_resolution": _real_ssot_cd_block(
                [{"variant_id": "A", "styleguide": REAL_GUIDE}]
            ),
            "directive_digest": SAME_DIGEST,
            "trial_start_directive_digest": SAME_DIGEST,
        },
        gamma_settings=[{"variant_id": "A", "styleguide": REAL_GUIDE}],
    )


@pytest.mark.parametrize(
    ("forcer", "expected_reason"),
    [
        (_force_resolution_mismatch, "resolution-mismatch"),
        (_force_cd_unresolvable, "cd-unresolvable-but-gary-resolved"),
        (_force_contract_violation_garbage, "contract-violation"),
        (_force_comparator_crash, "contract-violation"),
    ],
)
def test_ac4_divergence_raises_pre_dispatch(
    forcer: Any,
    expected_reason: str,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with pytest.raises(gary_act.GaryActError) as excinfo:
        forcer(tmp_path, monkeypatch)
    assert excinfo.value.tag == DIVERGENCE_TAG
    # The raised message carries the divergence reason for triage.
    assert expected_reason in str(excinfo.value)
    # Deterministic error-pause, never retryable.
    assert DIVERGENCE_TAG not in _RETRYABLE_DISPATCH_TAGS


def test_ac4_divergence_dispatches_nothing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Pre-spend witness: on a divergence, zero generative dispatch. We use a
    # capturing client and assert generate_calls stays empty across the raise.
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
    zpath = _titled_zip(tmp_path)
    monkeypatch.setattr(
        gary_act, "download_export", lambda url, *, output_dir, filename: str(zpath)
    )
    client = _CapturingClient()
    payload = {
        "slides": [{"slide_id": "s1", "title": "Only Slide"}],
        "export_dir": str(tmp_path / "exports"),
        "gamma_settings": [{"variant_id": "A", "styleguide": "parity-probe-guide"}],
        "cd_styleguide_resolution": block,
        "directive_digest": SAME_DIGEST,
        "trial_start_directive_digest": SAME_DIGEST,
    }
    with pytest.raises(gary_act.GaryActError) as excinfo:
        gary_act.generate_gamma_variants(payload, client=client)
    assert excinfo.value.tag == DIVERGENCE_TAG
    assert client.generate_calls == [], "a divergence halt must not dispatch Gamma"


# --- R1: the halt-path message carries the digest summary + makes no false claim -


def test_r1_divergence_message_carries_digests_and_no_false_ride_claim(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # R1 (SHOULD-FIX): on the Flip-B halt path dispatch stops PRE-contribution,
    # so Gary's parity receipt is NEVER persisted — the raised message must
    # therefore (a) carry a COMPACT DIGEST SUMMARY (the resolution + directive
    # digests held in scope at the raise site) so triage is possible from the
    # error alone, and (b) NOT claim the receipt "rides the contribution", which
    # is FALSE on the halt path (AC-4/D2 reachability contract).
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
    # Capture the ACTUAL receipt the raise site reads, so the assertion binds to
    # the exact digests the message must carry (no independent recomputation
    # that could drift from resolve_view["resolved_base"]).
    captured: dict[str, Any] = {}
    real_receipt = gary_act._styleguide_parity_receipt

    def _capture(payload: dict[str, Any], resolve_view: dict[str, Any]) -> dict[str, Any]:
        receipt = real_receipt(payload, resolve_view)
        captured["receipt"] = receipt
        return receipt

    monkeypatch.setattr(gary_act, "_styleguide_parity_receipt", _capture)

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
    msg = str(excinfo.value)
    receipt = captured["receipt"]
    assert excinfo.value.tag == DIVERGENCE_TAG
    assert receipt["reason"] == "resolution-mismatch"
    cd_resolution_digest = receipt["cd_resolution_digest"]
    gary_resolution_digest = receipt["gary_resolution_digest"]
    assert cd_resolution_digest and gary_resolution_digest
    assert cd_resolution_digest != gary_resolution_digest, "must be a genuine mismatch"
    # (a) both resolution digest VALUES are reachable from the error context.
    assert cd_resolution_digest in msg, "cd_resolution_digest missing from halt message"
    assert gary_resolution_digest in msg, "gary_resolution_digest missing from message"
    # The directive digest is also surfaced (compact summary is complete).
    assert SAME_DIGEST in msg
    # reason preserved.
    assert "resolution-mismatch" in msg
    # (b) NO false "rides/ride the ... receipt" claim on the halt path.
    lowered = msg.lower()
    assert "ride the" not in lowered, "halt message must not claim the receipt rides"
    assert "rides the" not in lowered, "halt message must not claim the receipt rides"


# --- R2: two-way-attested divergence (trial-start digest ABSENT) still raises ----


def test_r2_two_way_divergence_trial_start_absent_still_raises(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # E4 ruling witness at the flip surface: a divergence produced with
    # trial_start_directive_digest=None (only cd+gary directive digests present
    # and equal — TWO-way attestation) STILL fires Flip B. Proves S4 added no
    # three-way attestation gate; two-way suffices to halt on a genuine defect.
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
    with pytest.raises(gary_act.GaryActError) as excinfo:
        _run(
            tmp_path,
            monkeypatch,
            {
                "cd_styleguide_resolution": block,
                "directive_digest": SAME_DIGEST,
                # trial-start attestation ABSENT — two-way (cd+gary) only.
                "trial_start_directive_digest": None,
            },
            gamma_settings=[{"variant_id": "A", "styleguide": "parity-probe-guide"}],
        )
    assert excinfo.value.tag == DIVERGENCE_TAG
    assert "resolution-mismatch" in str(excinfo.value)


# --- AC-5: every tolerated state proceeds (anti-over-fire) -----------------------


def test_ac5_ok_match_proceeds(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    result, client = _run(
        tmp_path,
        monkeypatch,
        {
            "cd_styleguide_resolution": _real_ssot_cd_block(
                [{"variant_id": "A", "styleguide": REAL_GUIDE}]
            ),
            "directive_digest": SAME_DIGEST,
            "trial_start_directive_digest": SAME_DIGEST,
        },
        gamma_settings=[{"variant_id": "A", "styleguide": REAL_GUIDE}],
    )
    assert result["styleguide_parity"]["outcome"] == "ok"
    assert result["styleguide_parity"]["reason"] == "match"
    assert client.generate_calls, "ok/match must dispatch"


def test_ac5_ok_status_keyed_no_picks_proceeds(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Empty gamma_settings -> default-A, gary pickless; CD no_picks_at_authoring
    # -> ok/status-keyed-no-picks. NO raise (out of Flip A scope; not divergence).
    result, client = _run(
        tmp_path,
        monkeypatch,
        {"cd_styleguide_resolution": _real_ssot_cd_block(None)},
        gamma_settings=None,
    )
    assert result["styleguide_parity"]["outcome"] == "ok"
    assert result["styleguide_parity"]["reason"] == "status-keyed-no-picks"
    assert client.generate_calls, "status-keyed-no-picks must dispatch"


def test_ac5_gap_cd_saw_no_picks_proceeds(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    result, client = _run(
        tmp_path,
        monkeypatch,
        {
            "cd_styleguide_resolution": _real_ssot_cd_block(None),
            "directive_digest": SAME_DIGEST,
            "trial_start_directive_digest": SAME_DIGEST,
        },
        gamma_settings=[{"variant_id": "A", "styleguide": REAL_GUIDE}],
    )
    assert result["styleguide_parity"]["outcome"] == "expected-ordering-gap"
    assert result["styleguide_parity"]["reason"] == "cd-saw-no-picks"
    assert client.generate_calls


def test_ac5_gap_directive_drift_proceeds(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    result, client = _run(
        tmp_path,
        monkeypatch,
        {
            "cd_styleguide_resolution": _real_ssot_cd_block(
                [{"variant_id": "A", "styleguide": REAL_GUIDE}],
                directive_digest="0" * 64,
            ),
            "directive_digest": SAME_DIGEST,
            "trial_start_directive_digest": SAME_DIGEST,
        },
        gamma_settings=[{"variant_id": "A", "styleguide": REAL_GUIDE}],
    )
    assert result["styleguide_parity"]["outcome"] == "expected-ordering-gap"
    assert result["styleguide_parity"]["reason"] == "directive-drift"
    assert client.generate_calls


def test_ac5_gap_cd_schema_newer_proceeds(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    block = dict(
        _real_ssot_cd_block([{"variant_id": "A", "styleguide": REAL_GUIDE}]),
        schema_version=2,
    )
    result, client = _run(
        tmp_path,
        monkeypatch,
        {
            "cd_styleguide_resolution": block,
            "directive_digest": SAME_DIGEST,
            "trial_start_directive_digest": SAME_DIGEST,
        },
        gamma_settings=[{"variant_id": "A", "styleguide": REAL_GUIDE}],
    )
    assert result["styleguide_parity"]["outcome"] == "expected-ordering-gap"
    assert result["styleguide_parity"]["reason"] == "cd-schema-newer"
    assert client.generate_calls


def test_ac5_gap_cd_envelope_absent_legacy_proceeds(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # No CD styleguide_resolution at all (legacy/rewind-recovered bundle) ->
    # gap/cd-envelope-absent-legacy, NO raise, dispatch proceeds (F-802).
    result, client = _run(
        tmp_path,
        monkeypatch,
        {},
        gamma_settings=[{"variant_id": "A", "styleguide": REAL_GUIDE}],
    )
    assert result["styleguide_parity"]["outcome"] == "expected-ordering-gap"
    assert result["styleguide_parity"]["reason"] == "cd-envelope-absent-legacy"
    assert client.generate_calls, "legacy/rewind bundle must dispatch cleanly"


def test_ac5_explicit_none_cd_block_proceeds(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    result, client = _run(
        tmp_path,
        monkeypatch,
        {"cd_styleguide_resolution": None},
        gamma_settings=[{"variant_id": "A", "styleguide": REAL_GUIDE}],
    )
    assert result["styleguide_parity"]["outcome"] == "expected-ordering-gap"
    assert result["styleguide_parity"]["reason"] == "cd-envelope-absent-legacy"
    assert client.generate_calls
