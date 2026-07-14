from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace

import pytest

from app.marcus.lesson_plan.pass1_authority import (
    LEGACY_SCHEMA_VERSION,
    SCHEMA_VERSION,
    Pass1PlanAuthorityError,
    assert_receipt_matches_plan,
    finalize_plan_authority,
    validate_receipt,
)
from app.marcus.lesson_plan.pass1_source_span_catalog import (
    build_pass1_source_span_catalog,
)
from app.marcus.lesson_plan.slide_authority import canonical_source_content_digest
from app.models.pass1_source_section import (
    Pass1AuthenticatedSourceSection,
    canonical_extracted_content_digest,
)
from app.models.state.cache_state import CacheState
from app.models.state.run_state import RunState
from app.specialists.irene_pass1 import _act as pass1_act
from app.specialists.source_bundle import read_extracted_source_with_sections
from tests._helpers.pass1_bundle import write_primary_slide_bundle

SOURCE_TEXT = "Knowledge grows quickly. Static training is insufficient."


def _source_sections() -> tuple[Pass1AuthenticatedSourceSection, ...]:
    digest = canonical_source_content_digest(SOURCE_TEXT)
    return (
        Pass1AuthenticatedSourceSection(
            source_id=f"slides/slide-5-training.md|{digest}",
            source_content_digest=digest,
            extracted_content_digest=canonical_extracted_content_digest(SOURCE_TEXT),
            body=SOURCE_TEXT,
        ),
    )


def _projected_plan() -> dict[str, object]:
    sections = _source_sections()
    catalog = build_pass1_source_span_catalog(sections)
    entries = {entry.text: entry for entry in catalog.entries}
    selected = [
        entries["Knowledge grows quickly."],
        entries["Static training is insufficient."],
    ]
    return {
        "source_span_catalog_digest": catalog.catalog_digest,
        "plan_units": [
            {
                "unit_id": "u05",
                "scope_decision": "in-scope",
                "source_ref_ids": [entry.span_id for entry in selected],
                "source_refs": [entry.text for entry in selected],
                "cluster_id": "c-u05",
                "cluster_role": "head",
                "parent_slide_id": None,
            }
        ],
    }


def _legacy_plan() -> dict[str, object]:
    return {
        "plan_units": [
            {
                "unit_id": "u05",
                "scope_decision": "in-scope",
                "source_refs": ["Knowledge grows quickly."],
                "cluster_id": "c-u05",
                "cluster_role": "head",
                "parent_slide_id": None,
            }
        ]
    }


def _digest(value: object) -> str:
    encoded = json.dumps(
        value,
        sort_keys=True,
        ensure_ascii=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def test_model_response_duplicate_keys_fail_closed() -> None:
    raw = '{"plan_units":[],"plan_units":[{"unit_id":"u01"}]}'
    with pytest.raises(pass1_act.Pass1AuthorityError, match="duplicate JSON keys"):
        pass1_act.parse_pass1_response(raw)


def test_processor_v2_accepts_exactly_one_surplus_final_root_brace() -> None:
    authored = {
        "lesson_summary": "Complete authored candidate.",
        "plan_units": [
            {
                "unit_id": "u01",
                "title": "One",
                "learning_objective": "Explain one.",
                "scope_decision": "in-scope",
                "rationale": "Grounded.",
                "source_ref_ids": ["span:sha256:" + "a" * 64],
            }
        ],
        "collateral": {"declaration": "none"},
    }
    parsed = pass1_act.parse_pass1_response(json.dumps(authored) + "}")

    assert parsed["lesson_summary"] == authored["lesson_summary"]
    assert [unit["unit_id"] for unit in parsed["plan_units"]] == ["u01"]
    assert parsed["plan_units"][0]["source_ref_ids"] == authored["plan_units"][0][
        "source_ref_ids"
    ]
    assert all(unit["unit_id"] != "unit-1" for unit in parsed["plan_units"])


def test_processor_v2_accepts_final_nonwhitespace_surplus_brace() -> None:
    authored = {
        "lesson_summary": "Candidate.",
        "plan_units": [{"unit_id": "u01"}],
        "collateral": {"declaration": "none"},
    }
    parsed = pass1_act.parse_pass1_response(json.dumps(authored) + "\n \t}\r\n")
    assert parsed["lesson_summary"] == "Candidate."


@pytest.mark.parametrize(
    "suffix",
    ["}}", "}garbage", "]", ",", " another-value", "\n}\ntrailing prose"],
)
def test_processor_v2_rejects_every_other_trailing_suffix(suffix: str) -> None:
    raw = json.dumps(
        {
            "lesson_summary": "Candidate.",
            "plan_units": [{"unit_id": "u01"}],
            "collateral": {"declaration": "none"},
        }
    ) + suffix

    with pytest.raises(pass1_act.Pass1AuthorityError, match="structured JSON object"):
        pass1_act.parse_pass1_response(raw)


@pytest.mark.parametrize(
    "raw",
    [
        '{"plan_units":[{"unit_id":"u01"}]',
        '{"plan_units" [{"unit_id":"u01"}]}',
        '[{"unit_id":"u01"}]',
        "null",
        'prefix {"plan_units":[{"unit_id":"u01"}]}',
        '{"plan_units":[],"score":NaN}',
        '\u00a0{"plan_units": []}\u00a0',
    ],
)
def test_processor_v2_never_synthesizes_a_unit_for_invalid_framing(raw: str) -> None:
    with pytest.raises(pass1_act.Pass1AuthorityError, match="structured JSON object"):
        pass1_act.parse_pass1_response(raw)


def test_processor_v2_rejects_duplicate_nested_key_on_surplus_brace_path() -> None:
    raw = (
        '{"plan_units":[{"unit_id":"u01","unit_id":"u02"}],'
        '"collateral":{"declaration":"none"}}}'
    )
    with pytest.raises(pass1_act.Pass1AuthorityError, match="duplicate JSON keys"):
        pass1_act.parse_pass1_response(raw)


def test_amendment7_frozen_run_file_set_and_hashes_are_unchanged() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    trial_id = "30850735-dea3-4444-bc7b-513239eae55b"
    manifest_path = (
        repo_root
        / "_bmad-output"
        / "implementation-artifacts"
        / "evidence"
        / "workbook-live-hil"
        / trial_id
        / "frozen-run-sha256-manifest.v1.json"
    )
    baseline = json.loads(manifest_path.read_text(encoding="utf-8"))["files"]
    run_dir = repo_root / "runs" / trial_id
    current_paths = {
        path.relative_to(run_dir).as_posix()
        for path in run_dir.rglob("*")
        if path.is_file()
    }
    assert current_paths == set(baseline)
    for relative_path, expected_hash in baseline.items():
        assert hashlib.sha256((run_dir / relative_path).read_bytes()).hexdigest() == expected_hash


@pytest.mark.parametrize("surplus", [False, True])
def test_processor_v2_accepts_only_an_exact_full_json_fence(surplus: bool) -> None:
    authored = {
        "lesson_summary": "Fenced candidate.",
        "plan_units": [{"unit_id": "u01"}],
        "collateral": {"declaration": "none"},
    }
    body = json.dumps(authored) + ("}" if surplus else "")
    parsed = pass1_act.parse_pass1_response(f"```json\n{body}\n```")
    assert parsed["lesson_summary"] == "Fenced candidate."


@pytest.mark.parametrize(
    "raw",
    [
        'prose\n```json\n{"plan_units": []}\n```',
        '```json\n{"plan_units": []}\n```\nprose',
        '```JSON\n{"plan_units": []}\n```',
        '```json {"plan_units": []}```',
    ],
)
def test_processor_v2_rejects_nonexact_fence_wrappers(raw: str) -> None:
    with pytest.raises(pass1_act.Pass1AuthorityError, match="structured JSON object"):
        pass1_act.parse_pass1_response(raw)


def test_v2_receipt_binds_ids_projected_bytes_source_and_catalog() -> None:
    plan = _projected_plan()
    receipt = finalize_plan_authority(plan, source_sections=_source_sections())

    assert receipt["schema_version"] == SCHEMA_VERSION
    assert receipt["catalog_digest"] == plan["source_span_catalog_digest"]
    assert receipt["identities"][0]["source_ref_ids"] == plan["plan_units"][0][
        "source_ref_ids"
    ]
    assert receipt["identities"][0]["source_refs"] == plan["plan_units"][0][
        "source_refs"
    ]
    assert receipt["identities"][0]["source_id"] == _source_sections()[0].source_id
    assert_receipt_matches_plan(plan, receipt)


def test_v2_authority_revalidation_rejects_more_than_six_selected_spans() -> None:
    source_text = " ".join(f"Sentence {index}." for index in range(1, 8))
    digest = canonical_source_content_digest(source_text)
    sections = (
        Pass1AuthenticatedSourceSection(
            source_id=f"slides/slide-5-training.md|{digest}",
            source_content_digest=digest,
            extracted_content_digest=canonical_extracted_content_digest(source_text),
            body=source_text,
        ),
    )
    catalog = build_pass1_source_span_catalog(sections)
    expected_sentences = {f"Sentence {index}." for index in range(1, 8)}
    selected = [entry for entry in catalog.entries if entry.text in expected_sentences]
    assert len(selected) == 7
    plan = {
        "source_span_catalog_digest": catalog.catalog_digest,
        "plan_units": [
            {
                "unit_id": "u05",
                "scope_decision": "in-scope",
                "source_ref_ids": [entry.span_id for entry in selected],
                "source_refs": [entry.text for entry in selected],
                "cluster_id": "c-u05",
                "cluster_role": "head",
                "parent_slide_id": None,
            }
        ],
    }

    with pytest.raises(Pass1PlanAuthorityError, match="one to six|six source spans"):
        finalize_plan_authority(plan, source_sections=sections)


@pytest.mark.parametrize("mutation", ["substitute", "reorder"])
def test_v2_temporal_identity_rejects_id_substitution_or_reordering(
    mutation: str,
) -> None:
    prior = _projected_plan()
    receipt = finalize_plan_authority(prior, source_sections=_source_sections())
    candidate = deepcopy(prior)
    unit = candidate["plan_units"][0]
    if mutation == "substitute":
        unit["source_ref_ids"] = [unit["source_ref_ids"][1]]
        unit["source_refs"] = [unit["source_refs"][1]]
    else:
        unit["source_ref_ids"].reverse()
        unit["source_refs"].reverse()

    with pytest.raises(Pass1PlanAuthorityError, match="recycled"):
        finalize_plan_authority(
            candidate,
            source_sections=_source_sections(),
            prior_receipt=receipt,
        )


def test_v2_temporal_identity_rejects_catalog_substitution() -> None:
    prior = _projected_plan()
    receipt = finalize_plan_authority(prior, source_sections=_source_sections())
    candidate = deepcopy(prior)
    candidate["source_span_catalog_digest"] = "sha256:" + "e" * 64

    with pytest.raises(Pass1PlanAuthorityError, match="catalog"):
        finalize_plan_authority(
            candidate,
            source_sections=_source_sections(),
            prior_receipt=receipt,
        )


@pytest.mark.parametrize(
    ("field", "mutated"),
    [
        ("source_ref_ids", []),
        ("cluster_role", "Head"),
        ("parent_slide_id", "u99"),
    ],
)
def test_raw_refinement_identity_rejects_drift_before_normalization(
    field: str, mutated: object
) -> None:
    prior = _projected_plan()
    receipt = finalize_plan_authority(prior, source_sections=_source_sections())
    raw_unit = deepcopy(prior["plan_units"][0])
    raw_unit.pop("source_refs")
    raw_unit[field] = mutated

    with pytest.raises(pass1_act.Pass1AuthorityError, match=f"immutable {field}"):
        pass1_act.parse_pass1_response(
            json.dumps({"plan_units": [raw_unit]}), prior_receipt=receipt
        )


def test_v2_receipt_rejects_rehashed_selected_id_tampering() -> None:
    plan = _projected_plan()
    receipt = finalize_plan_authority(plan, source_sections=_source_sections())
    forged = deepcopy(receipt)
    forged["identities"][0]["source_ref_ids"][0] = "span:sha256:" + "d" * 64
    body = {key: value for key, value in forged.items() if key != "authority_digest"}
    forged["authority_digest"] = _digest(body)

    with pytest.raises(Pass1PlanAuthorityError, match="identity disagrees"):
        assert_receipt_matches_plan(plan, forged)


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        ("head_parent", "head.*parent"),
        ("invalid_source_id", "source identity"),
        ("misaligned_projection", "projected source references"),
    ],
)
def test_validate_receipt_rejects_rehashed_cross_field_corruption(
    mutation: str,
    message: str,
) -> None:
    receipt = finalize_plan_authority(_projected_plan(), source_sections=_source_sections())
    forged = deepcopy(receipt)
    row = forged["identities"][0]
    if mutation == "head_parent":
        row["parent_slide_id"] = "u99"
    elif mutation == "invalid_source_id":
        row["source_id"] = "not-an-authenticated-source"
    else:
        row["source_ref_ids"] = row["source_ref_ids"][:-1]
    body = {key: value for key, value in forged.items() if key != "authority_digest"}
    forged["authority_digest"] = _digest(body)

    with pytest.raises(Pass1PlanAuthorityError, match=message):
        validate_receipt(forged)


def test_validate_receipt_rejects_active_child_of_retired_parent() -> None:
    plan = _projected_plan()
    head = plan["plan_units"][0]
    child = deepcopy(head)
    child.update(
        {
            "unit_id": "u05i1",
            "cluster_role": "interstitial",
            "parent_slide_id": "u05",
        }
    )
    plan["plan_units"].append(child)
    receipt = finalize_plan_authority(plan, source_sections=_source_sections())
    forged = deepcopy(receipt)
    forged["identities"][0]["active"] = False
    body = {key: value for key, value in forged.items() if key != "authority_digest"}
    forged["authority_digest"] = _digest(body)

    with pytest.raises(Pass1PlanAuthorityError, match="active.*parent"):
        validate_receipt(forged)


def test_validate_receipt_requires_active_prefix_before_retired_history() -> None:
    plan = _projected_plan()
    second = deepcopy(plan["plan_units"][0])
    second["unit_id"] = "u06"
    second["cluster_id"] = "c-u06"
    plan["plan_units"].append(second)
    receipt = finalize_plan_authority(plan, source_sections=_source_sections())
    forged = deepcopy(receipt)
    forged["identities"][0]["active"] = False
    body = {key: value for key, value in forged.items() if key != "authority_digest"}
    forged["authority_digest"] = _digest(body)

    with pytest.raises(Pass1PlanAuthorityError, match="active identity follows retired"):
        validate_receipt(forged)


def test_receipt_reconciliation_rejects_plan_cluster_drift() -> None:
    plan = _projected_plan()
    head = plan["plan_units"][0]
    child = deepcopy(head)
    child.update(
        {
            "unit_id": "u05i1",
            "cluster_role": "interstitial",
            "parent_slide_id": "u05",
        }
    )
    plan["plan_units"].append(child)
    receipt = finalize_plan_authority(plan, source_sections=_source_sections())
    forged_plan = deepcopy(plan)
    forged_plan["plan_units"][1]["cluster_id"] = "different-cluster"
    forged_receipt = deepcopy(receipt)
    forged_receipt["plan_digest"] = _digest(forged_plan)
    body = {
        key: value for key, value in forged_receipt.items() if key != "authority_digest"
    }
    forged_receipt["authority_digest"] = _digest(body)

    with pytest.raises(Pass1PlanAuthorityError, match="cluster disagrees"):
        assert_receipt_matches_plan(forged_plan, forged_receipt)


def test_legacy_v1_is_readable_but_cannot_silently_upgrade_to_v2() -> None:
    legacy_plan = _legacy_plan()
    legacy_receipt = finalize_plan_authority(
        legacy_plan, source_sections=_source_sections()
    )
    assert legacy_receipt["schema_version"] == LEGACY_SCHEMA_VERSION
    assert validate_receipt(legacy_receipt) == legacy_receipt
    assert_receipt_matches_plan(legacy_plan, legacy_receipt)

    with pytest.raises(Pass1PlanAuthorityError, match="legacy-v1.*read-only"):
        finalize_plan_authority(
            _projected_plan(),
            source_sections=_source_sections(),
            prior_receipt=legacy_receipt,
        )


def test_legacy_v1_cannot_bind_a_projected_v2_plan() -> None:
    legacy_receipt = finalize_plan_authority(
        _legacy_plan(), source_sections=_source_sections()
    )
    with pytest.raises(Pass1PlanAuthorityError, match="legacy-v1.*read-only"):
        assert_receipt_matches_plan(_projected_plan(), legacy_receipt)


def test_production_refinement_rejects_legacy_v1_before_provider(tmp_path) -> None:
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    write_primary_slide_bundle(bundle, f"# Corpus\n\n{SOURCE_TEXT}")
    _extracted, sections = read_extracted_source_with_sections(
        {"bundle_reference": str(bundle)}
    )
    prior_plan = _legacy_plan()
    legacy_receipt = finalize_plan_authority(prior_plan, source_sections=sections)
    payload = {
        "mode": "pass-1",
        "run_id": "legacy-v1-read-only",
        "runs_root": str(tmp_path),
        "bundle_reference": str(bundle),
        "upstream_output": {"lesson_plan": prior_plan},
        "prior_plan_authority_receipt": legacy_receipt,
    }
    state = RunState(
        graph_version="v0.1-stub",
        temperature=0.0,
        cache_state=CacheState(
            cache_prefix=json.dumps(payload, sort_keys=True), entries_count=0
        ),
    )

    class _BombChat:
        def invoke(self, _messages: object) -> object:
            raise AssertionError("legacy-v1 refinement must stop before provider")

    with pytest.raises(pass1_act.Pass1AuthorityError, match="legacy-v1.*read-only"):
        pass1_act.act(
            state,
            handle=SimpleNamespace(chat=_BombChat()),
            model_id="bomb",
        )


def test_production_refinement_rejoins_prior_v2_authority_before_provider(
    tmp_path,
) -> None:
    bundle = tmp_path / "bundle-current-v2"
    bundle.mkdir()
    write_primary_slide_bundle(bundle, SOURCE_TEXT)
    _extracted, sections = read_extracted_source_with_sections(
        {"bundle_reference": str(bundle)}
    )
    catalog = build_pass1_source_span_catalog(sections)
    entries = {entry.text: entry for entry in catalog.entries}
    selected = [
        entries["Knowledge grows quickly."],
        entries["Static training is insufficient."],
    ]
    prior_plan = {
        "source_span_catalog_digest": catalog.catalog_digest,
        "plan_units": [
            {
                "unit_id": "u01",
                "scope_decision": "in-scope",
                "source_ref_ids": [entry.span_id for entry in selected],
                "source_refs": [entry.text for entry in selected],
                "cluster_id": "c-u01",
                "cluster_role": "head",
                "parent_slide_id": None,
            }
        ],
    }
    prior_receipt = finalize_plan_authority(prior_plan, source_sections=sections)
    forged_plan = deepcopy(prior_plan)
    forged_plan["plan_units"][0]["source_refs"][0] = "Rehashed non-source text."
    forged_receipt = deepcopy(prior_receipt)
    forged_receipt["plan_digest"] = _digest(forged_plan)
    forged_receipt["identities"][0]["source_refs"][0] = "Rehashed non-source text."
    body = {
        key: value for key, value in forged_receipt.items() if key != "authority_digest"
    }
    forged_receipt["authority_digest"] = _digest(body)
    payload = {
        "mode": "pass-1",
        "run_id": "current-v2-source-rejoin",
        "runs_root": str(tmp_path),
        "bundle_reference": str(bundle),
        "upstream_output": {"lesson_plan": forged_plan},
        "prior_plan_authority_receipt": forged_receipt,
    }
    state = RunState(
        graph_version="v0.1-stub",
        temperature=0.0,
        cache_state=CacheState(
            cache_prefix=json.dumps(payload, sort_keys=True), entries_count=0
        ),
    )

    class _BombChat:
        calls = 0

        def invoke(self, _messages: object) -> object:
            self.calls += 1
            raise AssertionError("stale current-v2 authority must stop before provider")

    chat = _BombChat()
    with pytest.raises(pass1_act.Pass1AuthorityError, match="selected IDs disagree"):
        pass1_act.act(
            state,
            handle=SimpleNamespace(
                chat=chat, model_config_digest="sha256:" + "a" * 64
            ),
            model_id="gpt-test",
        )

    assert chat.calls == 0
    assert not list((tmp_path / payload["run_id"]).glob("irene-pass1-call-*.v1.json"))


def test_rehashed_seven_span_prior_authority_stops_before_provider(tmp_path) -> None:
    source_text = " ".join(f"Sentence {index}." for index in range(1, 8))
    bundle = tmp_path / "bundle-seven-span-prior"
    bundle.mkdir()
    write_primary_slide_bundle(bundle, source_text)
    _extracted, sections = read_extracted_source_with_sections(
        {"bundle_reference": str(bundle)}
    )
    catalog = build_pass1_source_span_catalog(sections)
    expected = {f"Sentence {index}." for index in range(1, 8)}
    selected = [entry for entry in catalog.entries if entry.text in expected]
    assert len(selected) == 7
    prior_plan = {
        "source_span_catalog_digest": catalog.catalog_digest,
        "plan_units": [
            {
                "unit_id": "u01",
                "scope_decision": "in-scope",
                "source_ref_ids": [entry.span_id for entry in selected[:6]],
                "source_refs": [entry.text for entry in selected[:6]],
                "cluster_id": "c-u01",
                "cluster_role": "head",
                "parent_slide_id": None,
            }
        ],
    }
    prior_receipt = finalize_plan_authority(prior_plan, source_sections=sections)
    prior_plan["plan_units"][0]["source_ref_ids"].append(selected[6].span_id)
    prior_plan["plan_units"][0]["source_refs"].append(selected[6].text)
    prior_receipt["plan_digest"] = _digest(prior_plan)
    prior_receipt["identities"][0]["source_ref_ids"].append(selected[6].span_id)
    prior_receipt["identities"][0]["source_refs"].append(selected[6].text)
    receipt_body = {
        key: value for key, value in prior_receipt.items() if key != "authority_digest"
    }
    prior_receipt["authority_digest"] = _digest(receipt_body)
    run_id = "seven-span-prior-rejected"
    payload = {
        "mode": "pass-1",
        "run_id": run_id,
        "runs_root": str(tmp_path),
        "bundle_reference": str(bundle),
        "upstream_output": {"lesson_plan": prior_plan},
        "prior_plan_authority_receipt": prior_receipt,
    }
    state = RunState(
        graph_version="v0.1-stub",
        temperature=0.0,
        cache_state=CacheState(
            cache_prefix=json.dumps(payload, sort_keys=True), entries_count=0
        ),
    )

    class _BombChat:
        calls = 0

        def invoke(self, _messages: object) -> object:
            self.calls += 1
            raise AssertionError("seven-span prior authority must stop before provider")

    chat = _BombChat()
    with pytest.raises(pass1_act.Pass1AuthorityError, match="six source spans"):
        pass1_act.act(
            state,
            handle=SimpleNamespace(
                chat=chat, model_config_digest="sha256:" + "a" * 64
            ),
            model_id="gpt-test",
        )
    assert chat.calls == 0
    run_dir = tmp_path / run_id
    assert not run_dir.exists() or not list(run_dir.glob("irene-pass1-call-*.v1.json"))


def test_rehashed_retired_v2_history_rejoins_every_span_to_catalog() -> None:
    sections = _source_sections()
    catalog = build_pass1_source_span_catalog(sections)
    entries = {entry.text: entry for entry in catalog.entries}
    first_plan = {
        "source_span_catalog_digest": catalog.catalog_digest,
        "plan_units": [
            {
                "unit_id": unit_id,
                "scope_decision": "in-scope",
                "source_ref_ids": [entries[text].span_id],
                "source_refs": [text],
                "cluster_id": f"c-{unit_id}",
                "cluster_role": "head",
                "parent_slide_id": None,
            }
            for unit_id, text in (
                ("u01", "Knowledge grows quickly."),
                ("u02", "Static training is insufficient."),
            )
        ],
    }
    first_receipt = finalize_plan_authority(first_plan, source_sections=sections)
    current_plan = deepcopy(first_plan)
    current_plan["plan_units"] = current_plan["plan_units"][:1]
    current_receipt = finalize_plan_authority(
        current_plan, source_sections=sections, prior_receipt=first_receipt
    )
    retired = next(row for row in current_receipt["identities"] if not row["active"])
    retired["source_ref_ids"] = ["span:sha256:" + "f" * 64]
    receipt_body = {
        key: value for key, value in current_receipt.items() if key != "authority_digest"
    }
    current_receipt["authority_digest"] = _digest(receipt_body)

    with pytest.raises(Pass1PlanAuthorityError, match="unknown source span ID"):
        finalize_plan_authority(
            current_plan,
            source_sections=sections,
            prior_receipt=current_receipt,
        )
