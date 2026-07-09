"""Canonical-arc S1 — CD `styleguide_resolution` sibling-block emission (D3).

Spec: `_bmad-output/implementation-artifacts/canonical-arc-s1-cd-styleguide-resolution-emission.md`.

RED-first tests 1-4 (spec §RED-first plan) + the AC-7 protected-invariant
assertion, the AC-8 legacy-tolerance pin, and the RED-7 §06 fence pin (AC-3 —
GREEN before implementation, must STAY green after).

The block is produced by the DETERMINISTIC NECK — a pure sibling function
beside ``_canonicalize_cd_directive`` — and is unconditionally present in the
``_act`` output blob as a SIBLING of ``cd_directive`` (never inside it).
Not-yet-existing symbols are imported inside test bodies so collection stays
green pre-implementation (each RED test fails individually, by design).
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pytest

from app.models.state.cache_state import CacheState
from app.models.state.model_resolution_entry import ModelResolutionEntry
from app.models.state.run_state import RunState
from app.specialists.cd.graph import _act
from app.specialists.gary.styleguide_library import (
    GAMMA_STYLE_GUIDES_PATH,
    resolve_styleguide,
)

DEFAULT_GUIDE = "hil-2026-apc-crossroads-classic"
DEFAULT_PROVENANCE_PIN = (
    "authoring-time default; gary runtime seeds DEFAULT_VARIANT_PAIR until S2/S4"
)


def _canonical_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, ensure_ascii=True, separators=(",", ":"))


def _ssot_digest() -> str:
    return hashlib.sha256(GAMMA_STYLE_GUIDES_PATH.read_bytes()).hexdigest()


def _bundle_payload(tmp_path: Path, **extra: Any) -> str:
    bundle = tmp_path / "bundle"
    bundle.mkdir(exist_ok=True)
    (bundle / "extracted.md").write_text(
        "# Sample corpus\n\nHealthcare inflection-point lesson content.",
        encoding="utf-8",
    )
    return json.dumps({"bundle_reference": str(bundle), **extra})


def _build_state(cache_prefix: str) -> RunState:
    return RunState(
        graph_version="v0.1-stub",
        temperature=0.0,
        model_resolution_trail=[
            ModelResolutionEntry(
                level="per_specialist",
                requested="gpt-5",
                resolved="gpt-5",
                reason="test",
                timestamp="2026-01-01T00:00:00Z",
                cache_prefix_hash="c" * 64,
            )
        ],
        cache_state=CacheState(cache_prefix=cache_prefix, entries_count=0),
    )


def _fake_llm(monkeypatch: pytest.MonkeyPatch, rationale: str = "Verbatim rationale.") -> None:
    class _Resp:
        content = json.dumps(
            {
                "cd_directive": {
                    "experience_profile": "visual-led",
                    "creative_rationale": rationale,
                }
            }
        )
        usage_metadata = {"input_tokens": 10, "output_tokens": 8}

    class _Chat:
        def invoke(self, _: Any) -> _Resp:
            return _Resp()

    class _Handle:
        chat = _Chat()

    monkeypatch.setattr("app.specialists.cd.graph.make_chat_model", lambda **_: _Handle())


def _projection(
    picks: dict[str, str] | None,
    *,
    provenance: dict[str, Any] | None = None,
    directive_digest: str = "d" * 64,
) -> dict[str, Any]:
    gamma_settings = (
        [
            {"variant_id": variant, "styleguide": name}
            for variant, name in sorted((picks or {}).items())
        ]
        if picks
        else None
    )
    projection: dict[str, Any] = {
        "gamma_settings": gamma_settings,
        "directive_digest": directive_digest,
    }
    if provenance is not None:
        projection["styleguide_picker_provenance"] = provenance
    return projection


def _act_output(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, **payload_extra: Any) -> dict:
    _fake_llm(monkeypatch)
    state = _build_state(_bundle_payload(tmp_path, brief="x", **payload_extra))
    update = _act(state)
    return json.loads(update["cache_state"]["cache_prefix"])


# --- RED-1 (AC-2 resolved path) ---------------------------------------------


def test_contribution_carries_resolution_block(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    provenance = {
        "picked_at": "2026-07-06T00:00:00+00:00",
        "picker_version": "test",
        "ssot_sha256": _ssot_digest(),
        "picks": [{"variant_id": "A", "styleguide": DEFAULT_GUIDE}],
        "written_by": "styleguide_picker",
    }
    projection = _projection({"A": DEFAULT_GUIDE}, provenance=provenance)
    output = _act_output(
        monkeypatch, tmp_path, directive_projection=projection
    )

    # Sibling key, NEVER inside the load-bearing cd_directive (AC-3 fence).
    assert "styleguide_resolution" in output, "sibling styleguide_resolution block missing"
    assert "styleguide_resolution" not in output["cd_directive"]
    block = output["styleguide_resolution"]

    assert block["schema_version"] == 1
    assert block["status"] == "resolved"
    # Verbatim echo of the styleguide-carrying gamma_settings entries + provenance.
    assert block["input_picks"]["gamma_settings"] == [
        {"variant_id": "A", "styleguide": DEFAULT_GUIDE}
    ]
    assert block["input_picks"]["styleguide_picker_provenance"] == provenance
    # Bound guide carries the SSOT digest of the yaml the resolver read, plus
    # lifecycle-as-DATA (remediation T6; visibility only when declared).
    assert block["bound_guides"] == [
        {"name": DEFAULT_GUIDE, "ssot_digest": _ssot_digest(), "lifecycle": "permanent"}
    ]
    # Full resolver output per bound guide — the frozen base-layer field set.
    assert block["resolved"]["A"] == resolve_styleguide(DEFAULT_GUIDE)
    # resolution_digest = sha256 of canonical-JSON of `resolved`.
    assert block["resolution_digest"] == hashlib.sha256(
        _canonical_json(block["resolved"]).encode("utf-8")
    ).hexdigest()
    # directive_digest echoed from the projection.
    assert block["directive_digest"] == "d" * 64
    # AC-7 protected invariant: explicit, machine-checkable layering rule.
    assert block["layering_manifest"] == {
        "base_layer": "styleguide_defaults",
        "composition_rule": "source_derived_wins",
    }


def test_two_pick_ab_projection_binds_both_variants(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    projection = _projection({"A": DEFAULT_GUIDE, "B": DEFAULT_GUIDE})
    output = _act_output(monkeypatch, tmp_path, directive_projection=projection)
    block = output["styleguide_resolution"]
    assert block["status"] == "resolved"
    assert sorted(block["resolved"]) == ["A", "B"]
    assert [guide["name"] for guide in block["bound_guides"]] == [
        DEFAULT_GUIDE,
        DEFAULT_GUIDE,
    ]


# --- RED-2 (AC-2 no-picks presence record + F-202 default pin) ---------------


@pytest.mark.parametrize(
    "payload_extra",
    [
        {},  # projection key entirely absent (pre-S2 runs; directive-less)
        {"directive_projection": {"gamma_settings": None, "directive_digest": None}},
    ],
    ids=["projection-absent", "gamma-settings-null"],
)
def test_no_picks_emits_presence_record(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, payload_extra: dict[str, Any]
) -> None:
    output = _act_output(monkeypatch, tmp_path, **payload_extra)
    assert "styleguide_resolution" in output, (
        "block must be UNCONDITIONALLY present — no_picks_at_authoring is a "
        "presence record, never a missing key"
    )
    block = output["styleguide_resolution"]
    assert block["status"] == "no_picks_at_authoring"
    assert block["input_picks"] is None
    # F-202 (binding): the no-picks default binds the X5-ratified standard-A
    # guide with the exact provenance string.
    assert block["bound_guides"] == [
        {"name": DEFAULT_GUIDE, "ssot_digest": _ssot_digest(), "lifecycle": "permanent"}
    ]
    assert block["resolved"]["A"] == resolve_styleguide(DEFAULT_GUIDE)
    assert block["default_provenance"] == DEFAULT_PROVENANCE_PIN
    assert block["layering_manifest"]["composition_rule"] == "source_derived_wins"


def test_entries_without_styleguide_still_no_picks_but_echoed(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Inline-settings entries (no `styleguide` key) are genuinely pick-less —
    the default binds — but the entries are STILL echoed verbatim in
    `input_picks` (remediation T3: full-echo audit record, not picks-only)."""
    settings = [{"variant_id": "A", "theme": "explicit-no-styleguide"}]
    output = _act_output(
        monkeypatch,
        tmp_path,
        directive_projection={"gamma_settings": settings, "directive_digest": "e" * 64},
    )
    block = output["styleguide_resolution"]
    assert block["status"] == "no_picks_at_authoring"
    assert block["input_picks"]["gamma_settings"] == settings
    assert block["bound_guides"] == [
        {"name": DEFAULT_GUIDE, "ssot_digest": _ssot_digest(), "lifecycle": "permanent"}
    ]
    assert block["default_provenance"] == DEFAULT_PROVENANCE_PIN


# --- RED-3 (AC-2 unresolvable pick recorded, never raised) -------------------


def test_unresolvable_pick_recorded_not_raised(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    projection = _projection({"A": "no-such-styleguide-anywhere"})
    output = _act_output(monkeypatch, tmp_path, directive_projection=projection)
    # CD is load-bearing (§06 fails loud without it): the bad pick must be
    # RECORDED, never raised — cd_directive still lands.
    assert output["cd_directive"]["schema_version"] == "1.0"
    block = output["styleguide_resolution"]
    assert block["status"] == "unresolvable_pick"
    # Remediation T7: `errors` is a LIST (all failures, in pick order).
    assert block["errors"], "unresolvable_pick must carry error evidence"
    assert block["errors"][0]["tag"] == "gamma.styleguide.unknown"
    assert "no-such-styleguide-anywhere" in block["errors"][0]["message"]
    # The failing pick is still echoed for the S3 parity comparator.
    assert block["input_picks"]["gamma_settings"] == [
        {"variant_id": "A", "styleguide": "no-such-styleguide-anywhere"}
    ]


# --- Remediation T2 (review): variant-id vocabulary + collision honesty ------


def test_duplicate_variant_ids_are_unresolvable_not_last_wins() -> None:
    """T2 RED shape: case-colliding variant ids previously collapsed `resolved`
    (last-wins) while bound_guides doubled — internally inconsistent audit."""
    from app.specialists.cd.graph import _styleguide_resolution_from_projection

    projection = {
        "gamma_settings": [
            {"variant_id": "A", "styleguide": DEFAULT_GUIDE},
            {"variant_id": "a", "styleguide": DEFAULT_GUIDE},
        ],
        "directive_digest": "d" * 64,
    }
    block = _styleguide_resolution_from_projection(projection)
    assert block["status"] == "unresolvable_pick"
    assert block["errors"], "post-normalization collision must carry error evidence"
    assert any("collision" in (err.get("tag") or "") for err in block["errors"])


@pytest.mark.parametrize(
    "variant_id",
    ["C", "", "  ", None, 7],
    ids=["outside-vocab", "empty", "whitespace", "absent-none", "non-string"],
)
def test_invalid_variant_id_is_unresolvable(variant_id: Any) -> None:
    """T2 RED shape: non-{A,B} ids previously passed unvalidated (and falsy ids
    silently defaulted to 'A')."""
    from app.specialists.cd.graph import _styleguide_resolution_from_projection

    entry: dict[str, Any] = {"styleguide": DEFAULT_GUIDE}
    if variant_id is not None:
        entry["variant_id"] = variant_id
    block = _styleguide_resolution_from_projection(
        {"gamma_settings": [entry], "directive_digest": None}
    )
    assert block["status"] == "unresolvable_pick"
    assert block["errors"]
    assert any(
        "variant" in (err.get("tag") or "") for err in block["errors"]
    ), f"invalid variant_id {variant_id!r} must be recorded as error evidence"


# --- Remediation T3 (review): blank/non-string names + verbatim full echo ----


@pytest.mark.parametrize(
    "name_value",
    ["", "   ", 123, None, ["list"]],
    ids=["empty", "whitespace", "int", "none", "list"],
)
def test_blank_or_nonstring_styleguide_name_is_unresolvable(name_value: Any) -> None:
    """T3 RED shape: blank/whitespace/non-string `styleguide` values were
    silently reclassified as no-picks (default bound, evidence hidden)."""
    from app.specialists.cd.graph import _styleguide_resolution_from_projection

    block = _styleguide_resolution_from_projection(
        {
            "gamma_settings": [{"variant_id": "A", "styleguide": name_value}],
            "directive_digest": None,
        }
    )
    assert block["status"] == "unresolvable_pick"
    assert block["errors"], "invalid pick name must carry error evidence"
    # The honest record NEVER binds the default over a present-but-bad pick.
    assert block["default_provenance"] is None


def test_input_picks_echoes_all_gamma_settings_entries_verbatim() -> None:
    """T3 RED shape: the echo previously carried picks-only — inline-settings
    entries (no `styleguide` key) vanished from the audit record."""
    from app.specialists.cd.graph import _styleguide_resolution_from_projection

    settings = [
        {"variant_id": "A", "styleguide": DEFAULT_GUIDE},
        {"variant_id": "B", "theme": "inline-theme-only"},
    ]
    block = _styleguide_resolution_from_projection(
        {
            "gamma_settings": settings,
            "directive_digest": None,
            "styleguide_picker_provenance": None,
        }
    )
    assert block["input_picks"]["gamma_settings"] == settings
    # The inline-settings entry is echoed but is NOT a pick: A still resolves.
    assert block["status"] == "resolved"
    assert sorted(block["resolved"]) == ["A"]


# --- Remediation T4 (review): SSOT-failure honesty (incl. ssot_path param) ---


def test_no_picks_with_ssot_failure_is_unresolvable_with_null_provenance(
    tmp_path: Path,
) -> None:
    """T4 RED shape: no-picks + SSOT-load failure previously shipped
    `no_picks_at_authoring` with default_provenance asserting a binding that
    FAILED. Must be unresolvable_pick; default_provenance null (did not bind)."""
    from app.specialists.cd.graph import _styleguide_resolution_from_projection

    missing = tmp_path / "no-such-ssot.yaml"
    block = _styleguide_resolution_from_projection(None, ssot_path=missing)
    assert block["status"] == "unresolvable_pick"
    assert block["default_provenance"] is None
    assert block["bound_guides"] == []
    assert block["resolved"] == {}
    assert block["errors"], "SSOT load failure must carry error evidence"


def test_no_picks_with_malformed_ssot_is_unresolvable(tmp_path: Path) -> None:
    from app.specialists.cd.graph import _styleguide_resolution_from_projection

    bad_ssot = tmp_path / "gamma-style-guides.yaml"
    bad_ssot.write_text("style_guides: [", encoding="utf-8")
    block = _styleguide_resolution_from_projection(None, ssot_path=bad_ssot)
    assert block["status"] == "unresolvable_pick"
    assert block["default_provenance"] is None
    assert block["errors"]


def test_pick_with_ssot_failure_is_unresolvable(tmp_path: Path) -> None:
    from app.specialists.cd.graph import _styleguide_resolution_from_projection

    missing = tmp_path / "no-such-ssot.yaml"
    block = _styleguide_resolution_from_projection(
        {
            "gamma_settings": [{"variant_id": "A", "styleguide": DEFAULT_GUIDE}],
            "directive_digest": None,
        },
        ssot_path=missing,
    )
    assert block["status"] == "unresolvable_pick"
    assert block["errors"]


# --- Remediation T5 (review): digest + resolution from the SAME guarded read -


def test_ssot_digest_attests_the_bytes_resolution_parsed(tmp_path: Path) -> None:
    """T5: a custom ssot_path proves the digest and the resolved surface come
    from the same file read (no TOCTOU between digest and parse)."""
    from app.specialists.cd.graph import _styleguide_resolution_from_projection

    custom = tmp_path / "custom-ssot.yaml"
    custom.write_text(
        "style_guides:\n"
        "  custom-guide:\n"
        "    production_mode: api\n"
        "    lifecycle: candidate\n"
        "    theme:\n"
        "      id: themeid123\n",
        encoding="utf-8",
    )
    block = _styleguide_resolution_from_projection(
        {
            "gamma_settings": [{"variant_id": "A", "styleguide": "custom-guide"}],
            "directive_digest": None,
        },
        ssot_path=custom,
    )
    assert block["status"] == "resolved"
    assert block["resolved"]["A"] == {"production_mode": "api", "theme": "themeid123"}
    assert block["bound_guides"][0]["ssot_digest"] == hashlib.sha256(
        custom.read_bytes()
    ).hexdigest()


# --- Remediation T6 (review): lifecycle/visibility recorded as DATA ----------


def test_bound_guides_carry_lifecycle_and_visibility_as_data() -> None:
    """T6: deprecated/probe guides still resolve CLEAN at the audit point (no
    enforcement — that stays pick-time A-M1); lifecycle/visibility ride along
    as DATA in each bound_guides entry."""
    from app.specialists.cd.graph import _styleguide_resolution_from_projection

    block = _styleguide_resolution_from_projection(
        {
            "gamma_settings": [
                {"variant_id": "A", "styleguide": "videographic-glance-track"},
                {"variant_id": "B", "styleguide": "leg-c-part3-floor-probe"},
            ],
            "directive_digest": None,
        }
    )
    assert block["status"] == "resolved", "lifecycle is DATA, never enforcement here"
    by_name = {entry["name"]: entry for entry in block["bound_guides"]}
    assert by_name["videographic-glance-track"]["lifecycle"] == "deprecated"
    assert by_name["leg-c-part3-floor-probe"]["lifecycle"] == "permanent"
    assert by_name["leg-c-part3-floor-probe"]["visibility"] == "probe"
    # visibility is emitted only when the record declares one.
    assert "visibility" not in by_name["videographic-glance-track"]


# --- Remediation T7 (review): ALL failures recorded, in pick order -----------


def test_all_pick_failures_recorded_in_pick_order() -> None:
    """T7 RED shape: only the FIRST resolver error was retained (`error`
    singleton); now `errors` records every failure in pick order."""
    from app.specialists.cd.graph import _styleguide_resolution_from_projection

    block = _styleguide_resolution_from_projection(
        {
            "gamma_settings": [
                {"variant_id": "A", "styleguide": "missing-guide-one"},
                {"variant_id": "B", "styleguide": "missing-guide-two"},
            ],
            "directive_digest": None,
        }
    )
    assert block["status"] == "unresolvable_pick"
    assert [err["styleguide"] for err in block["errors"]] == [
        "missing-guide-one",
        "missing-guide-two",
    ]


# --- RED-4 (AC-1 determinism: byte-stable neck; provably LLM-free) -----------


def test_neck_determinism_byte_stable() -> None:
    from app.specialists.cd.graph import _styleguide_resolution_from_projection

    projection = _projection({"A": DEFAULT_GUIDE})
    first = _styleguide_resolution_from_projection(projection)
    second = _styleguide_resolution_from_projection(projection)
    assert _canonical_json(first) == _canonical_json(second)
    # And the no-picks default path is equally byte-stable.
    assert _canonical_json(_styleguide_resolution_from_projection(None)) == _canonical_json(
        _styleguide_resolution_from_projection(None)
    )


def test_resolution_block_is_llm_free(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Vary the fake LLM's creative output; the block must be byte-unchanged."""
    projection = _projection({"A": DEFAULT_GUIDE})

    _fake_llm(monkeypatch, rationale="First creative take.")
    first = json.loads(
        _act(_build_state(_bundle_payload(tmp_path, brief="x", directive_projection=projection)))[
            "cache_state"
        ]["cache_prefix"]
    )
    _fake_llm(monkeypatch, rationale="A completely different creative direction.")
    second = json.loads(
        _act(_build_state(_bundle_payload(tmp_path, brief="x", directive_projection=projection)))[
            "cache_state"
        ]["cache_prefix"]
    )
    assert first["cd_directive"]["creative_rationale"] != second["cd_directive"][
        "creative_rationale"
    ]
    assert _canonical_json(first["styleguide_resolution"]) == _canonical_json(
        second["styleguide_resolution"]
    )


# --- AC-8 legacy tolerance + schema_version discrimination -------------------


def test_legacy_cd_output_without_block_passes_readers() -> None:
    """A pre-S1 / rewind-recovered cd contribution (no block) passes the §06
    reader; `schema_version` discriminates new-format blocks (AC-8)."""
    from uuid import UUID

    from app.marcus.orchestrator.package_builders import run_builder_node
    from app.models.runtime.production_envelope import (
        ProductionEnvelope,
        SpecialistContribution,
    )

    trial_id = UUID("12345678-1234-4234-8234-123456789abc")
    envelope = ProductionEnvelope(trial_id=trial_id)
    envelope.add_contribution(
        SpecialistContribution.from_output(
            specialist_id="irene_pass1",
            output={
                "lesson_plan": {
                    "plan_units": [
                        {
                            "unit_id": "PU-1",
                            "title": "Unit",
                            "learning_objective": "Objective",
                            "scope_decision": "in-scope",
                        }
                    ]
                }
            },
            model_used="gpt-5-nano",
            node_id="04A",
        )
    )
    envelope.add_contribution(
        SpecialistContribution.from_output(
            specialist_id="cd",
            # LEGACY shape: no styleguide_resolution key at all.
            output={"cd_directive": {"experience_profile": "text-led"}},
            model_used="gpt-5-nano",
            node_id="4.75",
        )
    )
    updated = run_builder_node(node_id="06", production_envelope=envelope)
    assert updated.get_contribution("package_builder", node_id="06") is not None


def test_cd_return_state_pin_accepts_optional_block() -> None:
    """`CdReturn` (extra='forbid') gains the OPTIONAL sibling field — the pin
    is EXTENDED, never weakened (spec F-205)."""
    from app.specialists.cd.state import CdReturn

    model = CdReturn.model_validate(
        {
            "specialist_id": "cd",
            "verb": "proceed",
            "cd_directive": {"schema_version": "1.0"},
            "styleguide_resolution": {"schema_version": 1, "status": "resolved"},
        }
    )
    assert model.styleguide_resolution == {"schema_version": 1, "status": "resolved"}


# --- RED-7 (AC-3 §06 fence — GREEN before, must STAY green after) ------------


def test_06_fold_byte_identical_with_and_without_sibling_block() -> None:
    """§06's fold reads ONLY `cd_directive`; the sibling block must never
    change the rendered package (byte-stable regression pin, AC-3)."""
    from uuid import UUID

    from app.marcus.orchestrator.package_builders import run_builder_node
    from app.models.runtime.production_envelope import (
        ProductionEnvelope,
        SpecialistContribution,
    )

    fixture = (
        Path(__file__).resolve().parents[2]
        / "fixtures"
        / "integration"
        / "marcus"
        / "legacy_envelope_50b7d353.json"
    )
    raw = json.loads(fixture.read_text(encoding="utf-8-sig"))
    by_id = {c["specialist_id"]: c["output"] for c in raw["contributions"]}
    lesson_plan = by_id["irene_pass1"]["lesson_plan"]
    cd_directive = by_id["cd"]["cd_directive"]

    def _package(cd_output: dict[str, Any]) -> dict[str, Any]:
        envelope = ProductionEnvelope(
            trial_id=UUID("12345678-1234-4234-8234-123456789abc")
        )
        envelope.add_contribution(
            SpecialistContribution.from_output(
                specialist_id="irene_pass1",
                output={"lesson_plan": lesson_plan},
                model_used="gpt-5-nano",
                node_id="04A",
            )
        )
        envelope.add_contribution(
            SpecialistContribution.from_output(
                specialist_id="cd",
                output=cd_output,
                model_used="gpt-5-nano",
                node_id="4.75",
            )
        )
        updated = run_builder_node(node_id="06", production_envelope=envelope)
        contribution = updated.get_contribution("package_builder", node_id="06")
        assert contribution is not None
        return contribution.output

    without_block = _package({"cd_directive": cd_directive})
    with_block = _package(
        {
            "cd_directive": cd_directive,
            "styleguide_resolution": {
                "schema_version": 1,
                "status": "no_picks_at_authoring",
            },
        }
    )
    assert _canonical_json(without_block) == _canonical_json(with_block), (
        "§06 fold changed when the sibling styleguide_resolution block was "
        "present — the load-bearing experience-profile flow is FENCED (AC-3)"
    )


# --- AC-L: live witness (small-$, --run-live gated; first-run-stands) --------


@pytest.mark.llm_live
def test_cd_live_dispatch_emits_resolution_and_neck_reproduces_it(
    tmp_path: Path,
) -> None:
    """One REAL live CD dispatch with a real corpus payload: the block is
    present with `status` matching the projection, and the neck re-run on the
    captured inputs reproduces the block byte-identically (AC-L).

    --run-live gated (llm_live marker); NOT executed at dev time — the
    orchestrator runs the live leg at review. First-run-stands: no
    retry-to-green on the assertions below.

    Remediation T9 (review, blind+SOP F-305): skipping happens ONLY on
    explicit credential/arming absence — and that is enforced UPSTREAM by
    conftest (llm_live is deselected without --run-live; auto-skipped when
    OPENAI_API_KEY is unset/placeholder). In an ARMED run, ANY invocation
    failure FAILS this test — no exception-message substring skip that could
    vacuously mask a genuine dispatch defect.
    """
    from app.specialists.cd.graph import _styleguide_resolution_from_projection

    bundle = tmp_path / "bundle"
    bundle.mkdir()
    (bundle / "extracted.md").write_text(
        "# A Clinician at the Crossroads\n\n"
        "Healthcare delivery is at an inflection point: AI-assisted decision "
        "support is moving from pilot programs into daily clinical workflows, "
        "and clinicians must weigh augmentation against automation bias.",
        encoding="utf-8",
    )
    projection = _projection({"A": DEFAULT_GUIDE})
    state = _build_state(
        json.dumps(
            {
                "bundle_reference": str(bundle),
                "brief": "Design a visual-led directive for a short clinical lesson.",
                "directive_projection": projection,
            }
        )
    )
    # T9: NO try/except skip here — an invocation failure in an armed run is a
    # genuine dispatch defect and must FAIL (first-run-stands).
    update = _act(state)
    output = json.loads(update["cache_state"]["cache_prefix"])
    block = output["styleguide_resolution"]
    # Status matches the projection (a real single-pick projection => resolved).
    assert block["status"] == "resolved"
    assert [guide["name"] for guide in block["bound_guides"]] == [DEFAULT_GUIDE]
    # Neck re-run on the captured inputs reproduces the block byte-identically.
    reproduced = _styleguide_resolution_from_projection(projection)
    assert _canonical_json(reproduced) == _canonical_json(block)


# --- F-102 rider (AC-4): zero new logic in the dead-ceremony nodes -----------


def test_f102_rider_no_resolution_logic_in_dead_ceremony_nodes() -> None:
    """Production dispatch never resumes specialist sub-graphs: gate_decision /
    finalize / handoff NEVER execute. ALL S1 work must live in the _act/neck
    path — pin that the dead-ceremony nodes stay resolution-free."""
    import inspect

    from app.specialists.cd.graph import _finalize, _gate_decision, _handoff

    for handler in (_gate_decision, _finalize, _handoff):
        source = inspect.getsource(handler)
        assert "styleguide" not in source.lower(), (
            f"{handler.__name__} gained styleguide logic — F-102 rider violated"
        )
