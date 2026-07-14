from __future__ import annotations

import hashlib
import json
import shutil
import socket
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace

import pytest

from app.marcus.lesson_plan.pass1_authority import (
    Pass1PlanAuthorityError,
    assert_receipt_matches_plan,
)
from app.marcus.orchestrator import package_builders, workbook_wiring
from app.models.state.cache_state import CacheState
from app.models.state.run_state import RunState
from app.pass1_generation_lock import (
    Pass1GenerationLockError,
    pass1_generation_lock,
)
from app.specialists import source_bundle as source_bundle_module
from app.specialists.irene_pass1 import _act as pass1_act
from app.specialists.source_bundle import (
    SourceBundleError,
    read_extracted_source_sections,
    read_extracted_source_with_sections,
)
from tests._helpers.pass1_bundle import (
    write_primary_slide_bundle,
    write_source_bundle_manifest,
)

SOURCES = (
    ("slides/slide-5.md", "Knowledge grows quickly.\nStatic training is insufficient."),
    (
        "slides/slide-6.md",
        "Part 2 Summary & Knowledge Check\nUse tools for shaping the future of care.",
    ),
)
REPO_ROOT = Path(__file__).resolve().parents[3]


def _authority_digest(text: str) -> str:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _extracted_digest(text: str) -> str:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n").strip()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _unit(
    unit_id: str = "u06",
    *,
    anchor: str = "shaping the future of care",
    role: str = "head",
    parent: str | None = None,
) -> dict[str, object]:
    return {
        "unit_id": unit_id,
        "scope_decision": "in-scope",
        "source_refs": [anchor],
        "cluster_role": role,
        "parent_slide_id": parent,
    }


def test_duplicate_ids_fail_before_cluster_normalization() -> None:
    raw = json.dumps({"plan_units": [_unit(), _unit()]})
    with pytest.raises(pass1_act.Pass1AuthorityError, match="duplicate unit_id"):
        pass1_act.parse_pass1_response(raw)


@pytest.mark.parametrize(
    "anchor",
    [
        "shape the future of care",
        "Shaping the future of care",
        "shaping  the future of care",
        "shaping the future of care!",
    ],
)
def test_near_match_anchor_is_never_repaired(anchor: str) -> None:
    plan = {"plan_units": [_unit(anchor=anchor)]}
    before = deepcopy(plan)
    with pytest.raises(pass1_act.Pass1AuthorityError, match="exactly one"):
        pass1_act.validate_pass1_plan_authority(plan, source_sections=SOURCES)
    assert plan == before


def test_exact_anchor_passes_without_mutation() -> None:
    plan = {"plan_units": [_unit()]}
    before = deepcopy(plan)
    pass1_act.validate_pass1_plan_authority(plan, source_sections=SOURCES)
    assert plan == before


def test_temporal_unit_id_reuse_for_different_authority_fails() -> None:
    prior = {
        "plan_units": [
            _unit("u05", anchor="Knowledge grows quickly"),
            _unit(
                anchor="Static training is insufficient",
                role="interstitial",
                parent="u05",
            )
        ]
    }
    candidate = {"plan_units": [_unit()]}
    with pytest.raises(pass1_act.Pass1AuthorityError, match="recycled"):
        pass1_act.validate_pass1_plan_authority(
            candidate,
            source_sections=SOURCES,
            prior_plan=prior,
        )


def test_retained_identity_allows_nonidentity_edits() -> None:
    prior_unit = _unit()
    candidate_unit = {**prior_unit, "title": "Revised title", "rationale": "Revised"}
    pass1_act.validate_pass1_plan_authority(
        {"plan_units": [candidate_unit]},
        source_sections=SOURCES,
        prior_plan={"plan_units": [prior_unit]},
    )


def test_retired_identity_survives_a_to_b_to_c_and_cannot_be_recycled() -> None:
    plan_a = {
        "plan_units": [
            _unit("u05", anchor="Knowledge grows quickly"),
            _unit(
                anchor="Static training is insufficient",
                role="interstitial",
                parent="u05",
            )
        ]
    }
    receipt_a = pass1_act.validate_pass1_plan_authority(
        plan_a, source_sections=SOURCES
    )
    plan_b = {"plan_units": [_unit("u07")]}
    receipt_b = pass1_act.validate_pass1_plan_authority(
        plan_b,
        source_sections=SOURCES,
        prior_receipt=receipt_a,
    )
    assert any(
        row["unit_id"] == "u06" and row["active"] is False
        for row in receipt_b["identities"]
    )

    with pytest.raises(pass1_act.Pass1AuthorityError, match="cannot be restored"):
        pass1_act.validate_pass1_plan_authority(
            {"plan_units": [_unit("u06")]},
            source_sections=SOURCES,
            prior_receipt=receipt_b,
        )


def test_retired_identity_cannot_be_restored_with_identical_authority() -> None:
    plan_a = {"plan_units": [_unit("u06")]}
    receipt_a = pass1_act.validate_pass1_plan_authority(
        plan_a, source_sections=SOURCES
    )
    receipt_b = pass1_act.validate_pass1_plan_authority(
        {"plan_units": [_unit("u07")]},
        source_sections=SOURCES,
        prior_receipt=receipt_a,
    )
    with pytest.raises(pass1_act.Pass1AuthorityError, match="cannot be restored"):
        pass1_act.validate_pass1_plan_authority(
            plan_a,
            source_sections=SOURCES,
            prior_receipt=receipt_b,
        )


@pytest.mark.parametrize("decision", [None, "unknown", {"scope": "delegated"}])
def test_unknown_scope_decision_fails_before_authority_projection(
    decision: object,
) -> None:
    unit = _unit()
    if decision is None:
        unit.pop("scope_decision")
    else:
        unit["scope_decision"] = decision
    with pytest.raises(pass1_act.Pass1AuthorityError, match="scope_decision"):
        pass1_act.validate_pass1_plan_authority(
            {"plan_units": [unit]}, source_sections=SOURCES
        )


def test_supplied_prior_receipt_must_bind_actual_prior_plan() -> None:
    receipt = pass1_act.validate_pass1_plan_authority(
        {"plan_units": [_unit("u05", anchor="Knowledge grows quickly")]},
        source_sections=SOURCES,
    )
    different_prior = {"plan_units": [_unit("u06")]}
    with pytest.raises(pass1_act.Pass1AuthorityError, match="does not bind"):
        pass1_act.validate_pass1_plan_authority(
            {"plan_units": [_unit("u07")]},
            source_sections=SOURCES,
            prior_plan=different_prior,
            prior_receipt=receipt,
        )


def test_receipt_identity_fields_must_match_bound_plan() -> None:
    plan = {"plan_units": [_unit()]}
    receipt = pass1_act.validate_pass1_plan_authority(
        plan, source_sections=SOURCES
    )
    forged = deepcopy(receipt)
    forged["identities"][0]["source_refs"] = ["different authority"]
    body = {key: value for key, value in forged.items() if key != "authority_digest"}
    forged["authority_digest"] = "sha256:" + hashlib.sha256(
        json.dumps(
            body,
            sort_keys=True,
            ensure_ascii=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    with pytest.raises(Pass1PlanAuthorityError, match="identity disagrees"):
        assert_receipt_matches_plan(plan, forged)


def test_malformed_prior_receipt_fails_before_llm_invocation() -> None:
    payload = {
        "upstream_output": {"lesson_plan": {"plan_units": [_unit()]}},
        "prior_plan_authority_receipt": "not-a-receipt",
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
            raise AssertionError("LLM must not be invoked")

    with pytest.raises(pass1_act.Pass1AuthorityError, match="must be a current-format"):
        pass1_act.act(
            state,
            handle=SimpleNamespace(chat=_BombChat()),
            model_id="bomb",
        )


def test_missing_cumulative_receipt_fails_before_refinement_llm() -> None:
    payload = {"upstream_output": {"lesson_plan": {"plan_units": []}}}
    state = RunState(
        graph_version="v0.1-stub",
        temperature=0.0,
        cache_state=CacheState(
            cache_prefix=json.dumps(payload, sort_keys=True), entries_count=0
        ),
    )

    class _BombChat:
        def invoke(self, _messages: object) -> object:
            raise AssertionError("LLM must not be invoked")

    with pytest.raises(pass1_act.Pass1AuthorityError, match="missing cumulative"):
        pass1_act.act(
            state,
            handle=SimpleNamespace(chat=_BombChat()),
            model_id="bomb",
        )


def test_receipt_binds_exact_plan_and_rejects_tampering() -> None:
    plan = {"plan_units": [_unit()]}
    receipt = pass1_act.validate_pass1_plan_authority(
        plan, source_sections=SOURCES
    )
    assert_receipt_matches_plan(plan, receipt)

    tampered = deepcopy(receipt)
    tampered["identities"][0]["source_refs"] = ["shape the future of care"]
    with pytest.raises(Pass1PlanAuthorityError, match="digest mismatch"):
        assert_receipt_matches_plan(plan, tampered)


def test_anchor_set_must_converge_on_one_source() -> None:
    unit = _unit()
    unit["source_refs"] = [
        "Static training is insufficient",
        "shaping the future of care",
    ]
    with pytest.raises(pass1_act.Pass1AuthorityError, match="across source"):
        pass1_act.validate_pass1_plan_authority(
            {"plan_units": [unit]}, source_sections=SOURCES
        )


def test_interstitial_parent_must_be_an_existing_preceding_head() -> None:
    plan = {
        "plan_units": [
            _unit(
                anchor="Static training is insufficient",
                role="interstitial",
                parent="missing",
            )
        ]
    }
    with pytest.raises(pass1_act.Pass1AuthorityError, match="parent authority"):
        pass1_act.validate_pass1_plan_authority(plan, source_sections=SOURCES)


def test_interstitial_must_share_parent_source_and_cluster() -> None:
    head = _unit("u05", anchor="Knowledge grows quickly")
    head["cluster_id"] = "cluster-1"
    child = _unit(
        "u06",
        anchor="shaping the future of care",
        role="interstitial",
        parent="u05",
    )
    child["cluster_id"] = "cluster-1"
    with pytest.raises(pass1_act.Pass1AuthorityError, match="source disagrees"):
        pass1_act.validate_pass1_plan_authority(
            {"plan_units": [head, child]}, source_sections=SOURCES
        )

    child["source_refs"] = ["Static training is insufficient"]
    child["cluster_id"] = "cluster-2"
    with pytest.raises(pass1_act.Pass1AuthorityError, match="cluster disagrees"):
        pass1_act.validate_pass1_plan_authority(
            {"plan_units": [head, child]}, source_sections=SOURCES
        )


def test_refinement_prompt_declares_durable_identity_contract() -> None:
    _system, refinement = pass1_act.assemble_pass1_prompt(
        {"upstream_output": {"lesson_plan": {"plan_units": []}}},
        extracted_source="Source.",
    )
    _system, creation = pass1_act.assemble_pass1_prompt(
        {}, extracted_source="Source."
    )
    assert "Durable identity contract for this refinement" in refinement
    assert "removed ID is retired forever" in refinement
    assert "Durable identity contract for this refinement" not in creation


def test_source_bundle_sections_follow_declared_metadata_boundaries(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    (bundle / "metadata.json").write_text(
        json.dumps(
            {
                "provenance": [
                    {
                        "ref_id": "src-check",
                        "ref": "assessments/check.md",
                        "role": "supporting",
                        "section_title": "check",
                    },
                    {
                        "ref_id": "src-slide-5",
                        "kind": "local_file",
                        "ref": "slides/slide-5-five.md",
                        "role": "primary",
                        "section_title": "slide-5",
                    },
                    {
                        "ref_id": "src-slide-6",
                        "kind": "local_file",
                        "ref": "slides/slide-6-six.md",
                        "role": "primary",
                        "section_title": "slide-6",
                    },
                ],
                "source_authority": [
                    {
                        "source_id": "src-slide-5",
                        "path": "slides/slide-5-five.md",
                        "source_content_digest": _authority_digest("Five body"),
                        "extracted_content_digest": _extracted_digest("Five body"),
                    },
                    {
                        "source_id": "src-slide-6",
                        "path": "slides/slide-6-six.md",
                        "source_content_digest": _authority_digest(
                            "Six body with an internal ## heading\n### slide-5"
                        ),
                        "extracted_content_digest": _extracted_digest(
                            "Six body with an internal ## heading\n### slide-5"
                        ),
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
    (bundle / "extracted.md").write_text(
        "# Bundle\n\n## slide-5\nFive body\n\n"
        "## slide-6\nSix body with an internal ## heading\n### slide-5\n",
        encoding="utf-8",
    )
    write_source_bundle_manifest(bundle)
    sections = read_extracted_source_sections(
        {"source_bundle": {"bundle_reference": str(bundle)}}
    )
    assert tuple((section.source_id, section.body) for section in sections) == (
        (
            "slides/slide-5-five.md|sha256:" + _authority_digest("Five body"),
            "Five body\n\n",
        ),
        (
            "slides/slide-6-six.md|sha256:"
            + _authority_digest("Six body with an internal ## heading\n### slide-5"),
            "Six body with an internal ## heading\n### slide-5\n",
        ),
    )


def test_source_bundle_requires_metadata_for_per_slide_authority(
    tmp_path: Path,
) -> None:
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    (bundle / "extracted.md").write_text("Source body", encoding="utf-8")
    with pytest.raises(SourceBundleError, match="unreadable or unsafe"):
        read_extracted_source_sections(
            {"source_bundle": {"bundle_reference": str(bundle)}}
        )


def test_source_bundle_rejects_duplicate_metadata_keys(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    (bundle / "metadata.json").write_text(
        '{"provenance":[],"provenance":[],"sme_refs":[]}',
        encoding="utf-8",
    )
    (bundle / "extracted.md").write_text("## slide\nBody\n", encoding="utf-8")
    write_source_bundle_manifest(bundle)

    with pytest.raises(SourceBundleError, match="unreadable"):
        read_extracted_source_sections(
            {"source_bundle": {"bundle_reference": str(bundle)}}
        )


def test_source_bundle_accepts_unused_nonlocal_supporting_authority(
    tmp_path: Path,
) -> None:
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    body = "Primary body"
    (bundle / "metadata.json").write_text(
        json.dumps(
            {
                "provenance": [
                    {
                        "ref_id": "src-slide",
                        "kind": "local_file",
                        "ref": "slides/slide-1-primary.md",
                        "role": "primary",
                        "section_title": "slide",
                    },
                    {
                        "ref_id": "src-url",
                        "kind": "url",
                        "ref": "https://example.test/support",
                        "role": "supporting",
                        "section_title": "",
                    },
                ],
                "source_authority": [
                    {
                        "source_id": "src-slide",
                        "path": "slides/slide-1-primary.md",
                        "source_content_digest": _authority_digest(body),
                        "extracted_content_digest": _extracted_digest(body),
                    },
                    {
                        "source_id": "src-url",
                        "path": None,
                        "source_content_digest": _authority_digest("support"),
                        "extracted_content_digest": _extracted_digest("support"),
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
    (bundle / "extracted.md").write_text(
        f"## slide\n{body}\n", encoding="utf-8"
    )
    write_source_bundle_manifest(bundle)

    sections = read_extracted_source_sections({"bundle_reference": str(bundle)})
    assert tuple((section.source_id, section.body) for section in sections) == (
        (f"slides/slide-1-primary.md|sha256:{_authority_digest(body)}", f"{body}\n"),
    )


def test_source_bundle_rejects_tampered_extracted_section(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    write_primary_slide_bundle(bundle, "Original anchor")
    (bundle / "extracted.md").write_text(
        "## slide-1\nFabricated anchor\n", encoding="utf-8"
    )

    with pytest.raises(SourceBundleError, match="does not bind") as excinfo:
        read_extracted_source_sections({"bundle_reference": str(bundle)})

    assert excinfo.value.tag == "source.bundle.manifest-invalid"


def test_source_bundle_rejects_conflicting_bundle_references(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    first.mkdir()
    second.mkdir()
    write_primary_slide_bundle(first, "First")
    write_primary_slide_bundle(second, "Second")

    with pytest.raises(SourceBundleError, match="conflicting") as excinfo:
        read_extracted_source_sections(
            {
                "bundle_reference": str(first),
                "upstream_output": {"bundle_reference": str(second)},
            }
        )

    assert excinfo.value.tag == "source.bundle.reference-ambiguous"


def test_source_bundle_rejects_duplicate_primary_refs(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    body = "First body"
    (bundle / "metadata.json").write_text(
        json.dumps(
            {
                "provenance": [
                    {
                        "ref_id": "src-slide",
                        "kind": "local_file",
                        "ref": "slides/slide-1-primary.md",
                        "role": "primary",
                        "section_title": "first",
                    },
                    {
                        "ref_id": "src-slide",
                        "kind": "local_file",
                        "ref": "slides/slide-1-primary.md",
                        "role": "primary",
                        "section_title": "second",
                    },
                ],
                "source_authority": [
                    {
                        "source_id": "src-slide",
                        "path": "slides/slide-1-primary.md",
                        "source_content_digest": _authority_digest(body),
                        "extracted_content_digest": _extracted_digest(body),
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    (bundle / "extracted.md").write_text(
        "## first\nFirst body\n## second\nSecond body\n", encoding="utf-8"
    )
    write_source_bundle_manifest(bundle)

    with pytest.raises(SourceBundleError, match="primary refs are ambiguous"):
        read_extracted_source_sections({"bundle_reference": str(bundle)})


def test_prompt_text_and_sections_share_one_extracted_snapshot(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    (bundle / "metadata.json").write_text(
        json.dumps(
            {
                "provenance": [
                    {
                        "ref_id": "src-slide-5",
                        "kind": "local_file",
                        "ref": "slides/slide-5-five.md",
                        "role": "primary",
                        "section_title": "slide-5",
                    },
                ],
                "source_authority": [
                    {
                        "source_id": "src-slide-5",
                        "path": "slides/slide-5-five.md",
                        "source_content_digest": _authority_digest("One immutable body"),
                        "extracted_content_digest": _extracted_digest(
                            "One immutable body"
                        ),
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    (bundle / "extracted.md").write_text(
        "## slide-5\nOne immutable body\n", encoding="utf-8"
    )
    write_source_bundle_manifest(bundle)
    original_read = source_bundle_module._read_contained_regular_bytes
    extracted_reads = 0

    def _counted_read(root: Path, path: Path, label: str) -> bytes:
        nonlocal extracted_reads
        if path.name == "extracted.md":
            extracted_reads += 1
        return original_read(root=root, path=path, label=label)

    monkeypatch.setattr(
        source_bundle_module, "_read_contained_regular_bytes", _counted_read
    )
    text, sections = read_extracted_source_with_sections(
        {"source_bundle": {"bundle_reference": str(bundle)}}
    )
    assert extracted_reads == 1
    assert text == "## slide-5\nOne immutable body\n"
    assert tuple((section.source_id, section.body) for section in sections) == (
        (
            "slides/slide-5-five.md|sha256:"
            + _authority_digest("One immutable body"),
            "One immutable body\n",
        ),
    )


def test_supporting_heading_does_not_truncate_primary_slide(
    tmp_path: Path,
) -> None:
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    (bundle / "metadata.json").write_text(
        json.dumps(
            {
                "provenance": [
                    {
                        "ref_id": "src-slide",
                        "kind": "local_file",
                        "ref": "slides/slide-1-primary.md",
                        "role": "primary",
                        "section_title": "slide",
                    },
                    {
                        "ref_id": "src-support",
                        "ref": "notes/support.md",
                        "role": "supporting",
                        "section_title": "support",
                    },
                ],
                "source_authority": [
                    {
                        "source_id": "src-slide",
                        "path": "slides/slide-1-primary.md",
                        "source_content_digest": _authority_digest(
                            "Primary body\n## support\nStill primary body"
                        ),
                        "extracted_content_digest": _extracted_digest(
                            "Primary body\n## support\nStill primary body"
                        ),
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    (bundle / "extracted.md").write_text(
        "## slide\nPrimary body\n## support\nStill primary body\n",
        encoding="utf-8",
    )
    write_source_bundle_manifest(bundle)

    sections = read_extracted_source_sections(
        {"source_bundle": {"bundle_reference": str(bundle)}}
    )
    assert tuple((section.source_id, section.body) for section in sections) == (
        (
            "slides/slide-1-primary.md|sha256:"
            + _authority_digest("Primary body\n## support\nStill primary body"),
            "Primary body\n## support\nStill primary body\n",
        ),
    )


def test_source_sections_use_explicit_titles_and_stop_at_non_slide_boundaries(
    tmp_path: Path,
) -> None:
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    (bundle / "metadata.json").write_text(
        json.dumps(
            {
                "provenance": [
                    {
                        "ref_id": "src-slide-1",
                        "kind": "local_file",
                        "ref": "slides/slide-1-primary.md",
                        "role": "primary",
                        "section_title": "my slide",
                    },
                    {
                        "ref_id": "src-notes",
                        "kind": "local_file",
                        "ref": "notes/extra.md",
                        "role": "primary",
                        "section_title": "extra notes",
                    },
                    {
                        "ref_id": "src-slide-2",
                        "kind": "local_file",
                        "ref": "slides/slide-2-next.md",
                        "role": "primary",
                        "section_title": "Next Slide",
                    },
                ],
                "source_authority": [
                    {
                        "source_id": "src-slide-1",
                        "path": "slides/slide-1-primary.md",
                        "source_content_digest": _authority_digest("Slide-only anchor"),
                        "extracted_content_digest": _extracted_digest(
                            "Slide-only anchor"
                        ),
                    },
                    {
                        "source_id": "src-notes",
                        "path": "notes/extra.md",
                        "source_content_digest": _authority_digest("Notes-only anchor"),
                        "extracted_content_digest": _extracted_digest(
                            "Notes-only anchor"
                        ),
                    },
                    {
                        "source_id": "src-slide-2",
                        "path": "slides/slide-2-next.md",
                        "source_content_digest": _authority_digest("Next-only anchor"),
                        "extracted_content_digest": _extracted_digest(
                            "Next-only anchor"
                        ),
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
    (bundle / "extracted.md").write_text(
        "## my slide\nSlide-only anchor\n"
        "## extra notes\nNotes-only anchor\n"
        "## Next Slide\nNext-only anchor\n",
        encoding="utf-8",
    )
    write_source_bundle_manifest(bundle)
    sections = read_extracted_source_sections(
        {"bundle_reference": str(bundle)}
    )
    assert tuple((section.source_id, section.body) for section in sections) == (
        (
            "slides/slide-1-primary.md|sha256:"
            + _authority_digest("Slide-only anchor"),
            "Slide-only anchor\n",
        ),
        (
            "slides/slide-2-next.md|sha256:" + _authority_digest("Next-only anchor"),
            "Next-only anchor\n",
        ),
    )


def test_authority_receipt_writer_ignores_predictable_temp_symlink(
    tmp_path: Path,
) -> None:
    run_id = "run-safe-receipt"
    run_dir = tmp_path / run_id
    run_dir.mkdir()
    external = tmp_path / "external.json"
    external.write_text("do not overwrite", encoding="utf-8")
    predictable = run_dir / "irene-pass1.plan-authority.json.tmp"
    try:
        predictable.symlink_to(external)
    except OSError as exc:
        pytest.skip(f"symlink unavailable: {exc}")
    receipt = pass1_act.validate_pass1_plan_authority(
        {"plan_units": [_unit()]}, source_sections=SOURCES
    )
    path = pass1_act.write_plan_authority_receipt(
        receipt, run_id=run_id, runs_root=tmp_path
    )
    assert external.read_text(encoding="utf-8") == "do not overwrite"
    assert path.is_file() and not path.is_symlink()


def test_current_plan_artifact_failure_rolls_back_every_coordinate(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    run_id = "run-transactional-plan"
    run_dir = tmp_path / run_id
    run_dir.mkdir()
    originals = {
        run_dir / "irene-pass1.md": b"old markdown",
        run_dir / "irene-pass1.lesson-plan.json": b'{"old":true}',
        run_dir / "irene-pass1.plan-authority.json": b'{"old":"receipt"}',
    }
    for path, raw in originals.items():
        path.write_bytes(raw)

    def _fail_receipt(*_args: object, **_kwargs: object) -> Path:
        raise pass1_act.Pass1AuthorityError("receipt publish failed")

    monkeypatch.setattr(pass1_act, "write_plan_authority_receipt", _fail_receipt)
    with pytest.raises(pass1_act.Pass1AuthorityError, match="receipt publish failed"):
        pass1_act.write_current_plan_artifacts(
            {"plan_units": [_unit()]},
            {"schema_version": "pass1-plan-authority.v1"},
            run_id=run_id,
            runs_root=tmp_path,
        )

    assert {path: path.read_bytes() for path in originals} == originals


def test_failure_after_receipt_publication_rolls_back_receipt_last(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    run_id = "run-receipt-published-rollback"
    run_dir = tmp_path / run_id
    run_dir.mkdir()
    originals = {
        run_dir / "irene-pass1.md": b"old markdown",
        run_dir / "irene-pass1.lesson-plan.json": b'{"old":true}',
        run_dir / "irene-pass1.plan-authority.json": b'{"old":"receipt"}',
    }
    for path, raw in originals.items():
        path.write_bytes(raw)
    real_fsync = pass1_act._fsync_directory
    flush_count = 0

    def _fail_current_receipt_flush(path: Path) -> None:
        nonlocal flush_count
        flush_count += 1
        if flush_count == 4:
            raise OSError("receipt directory flush failed")
        real_fsync(path)

    monkeypatch.setattr(pass1_act, "_fsync_directory", _fail_current_receipt_flush)
    with pytest.raises(
        pass1_act.Pass1AuthorityError, match="artifact publication failed"
    ):
        pass1_act.write_current_plan_artifacts(
            {"plan_units": [_unit()]},
            {"schema_version": "pass1-plan-authority.v1"},
            run_id=run_id,
            runs_root=tmp_path,
        )

    assert {path: path.read_bytes() for path in originals} == originals


def test_overlapping_plan_publication_fails_before_snapshot(
    tmp_path: Path,
) -> None:
    run_id = "run-overlapping-plan-publication"
    run_dir = tmp_path / run_id
    run_dir.mkdir()

    with pass1_generation_lock(run_dir), pytest.raises(
        pass1_act.Pass1AuthorityError, match="generation lock"
    ):
        pass1_act.write_current_plan_artifacts(
            {"plan_units": [_unit()]},
            {"schema_version": "pass1-plan-authority.v1"},
            run_id=run_id,
            runs_root=tmp_path,
        )

    assert not (run_dir / "irene-pass1.plan-authority.json").exists()


def test_overlapping_pass1_act_fails_before_provider_invocation(tmp_path: Path) -> None:
    run_id = "run-overlapping-pass1-act"
    run_dir = tmp_path / run_id
    run_dir.mkdir()
    payload = {"mode": "pass-1", "run_id": run_id, "runs_root": str(tmp_path)}
    state = RunState(
        graph_version="v0.1-stub",
        temperature=0.0,
        cache_state=CacheState(
            cache_prefix=json.dumps(payload, sort_keys=True), entries_count=0
        ),
    )

    class _CountingChat:
        calls = 0

        def invoke(self, _messages: object) -> object:
            self.calls += 1
            raise AssertionError("provider must not be invoked")

    chat = _CountingChat()
    with pass1_generation_lock(run_dir), pytest.raises(
        pass1_act.Pass1AuthorityError, match="generation lock"
    ):
        pass1_act.act(
            state, handle=SimpleNamespace(chat=chat), model_id="lock-test"
        )

    assert chat.calls == 0


def test_generation_lock_rejects_hard_link_coordinate(tmp_path: Path) -> None:
    run_dir = tmp_path / "run-hard-link-lock"
    run_dir.mkdir()
    external = tmp_path / "external-lock-alias"
    external.write_bytes(b"")
    lock_path = tmp_path / f".{run_dir.name}.irene-pass1.generation.lock"
    try:
        lock_path.hardlink_to(external)
    except OSError as exc:
        pytest.skip(f"hard links unavailable: {exc}")

    with pytest.raises(
        Pass1GenerationLockError, match="unavailable"
    ), pass1_generation_lock(run_dir):
        pass

    assert external.read_bytes() == b""


def test_interrupted_plan_publish_leaves_no_commit_marker(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    run_id = "run-interrupted-plan"
    run_dir = tmp_path / run_id
    run_dir.mkdir()
    (run_dir / "irene-pass1.md").write_text("old", encoding="utf-8")
    (run_dir / "irene-pass1.lesson-plan.json").write_text(
        '{"old":true}', encoding="utf-8"
    )
    receipt_path = run_dir / "irene-pass1.plan-authority.json"
    receipt_path.write_text('{"old":"receipt"}', encoding="utf-8")
    real_replace = pass1_act.os.replace

    def _interrupt(source: object, target: object) -> None:
        if Path(target).name == "irene-pass1.lesson-plan.json":
            raise SystemExit("simulated process exit")
        real_replace(source, target)

    monkeypatch.setattr(pass1_act.os, "replace", _interrupt)
    with pytest.raises(SystemExit, match="simulated process exit"):
        pass1_act.write_current_plan_artifacts(
            {"plan_units": [_unit()]},
            {"schema_version": "pass1-plan-authority.v1"},
            run_id=run_id,
            runs_root=tmp_path,
        )

    assert not receipt_path.exists()


def test_frozen_failure_rejects_upstream_with_zero_downstream_effects(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    frozen = REPO_ROOT / "runs" / "a28aa15a-fc80-46ae-b05a-09ac864829bb"
    copied = tmp_path / "frozen-copy"
    shutil.copytree(frozen, copied)
    before = {
        path.relative_to(copied).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in copied.rglob("*")
        if path.is_file()
    }
    assert before["error-pause.json"] == (
        "4d9bc6f4c1c4ef5f662f6607326402dc741f1e845dd5ec1034f49283cc4fa6bc"
    )
    assert before["run.json"] == (
        "3935b017d343bfd5c8bcdd1b7998d07ef82238ab74fa5031b6a1df60b90bc50f"
    )
    trial = json.loads((copied / "run.json").read_text(encoding="utf-8"))
    irene = {
        row["node_id"]: row["output"]["lesson_plan"]
        for row in trial["production_envelope"]["contributions"]
        if row["specialist_id"] == "irene_pass1"
    }
    course_root = Path(trial["corpus_path"])
    slides = sorted((course_root / "slides").glob("*.md"))
    source_sections = tuple(
        (
            f"{path.relative_to(course_root).as_posix()}|"
            f"{_authority_digest(path.read_text(encoding='utf-8'))}",
            path.read_text(encoding="utf-8"),
        )
        for path in slides
    )
    prior_receipt = pass1_act.validate_pass1_plan_authority(
        irene["04A"], source_sections=source_sections
    )
    bundle = tmp_path / "current-bundle"
    bundle.mkdir()
    provenance: list[dict[str, object]] = []
    source_authority: list[dict[str, object]] = []
    extracted_parts = ["# Source bundle: frozen Amendment-5 regression", ""]
    for index, path in enumerate(slides, start=1):
        relative = path.relative_to(course_root).as_posix()
        source_id = f"src-{index:03d}"
        title = path.stem
        body = path.read_text(encoding="utf-8")
        provenance.append(
            {
                "ref_id": source_id,
                "kind": "local_file",
                "ref": relative,
                "role": "primary",
                "section_title": title,
            }
        )
        source_authority.append(
            {
                "source_id": source_id,
                "path": relative,
                "source_content_digest": _authority_digest(body),
                "extracted_content_digest": _extracted_digest(body),
            }
        )
        extracted_parts.extend([f"## {title}", "", body.strip(), ""])
    (bundle / "metadata.json").write_text(
        json.dumps(
            {"provenance": provenance, "source_authority": source_authority}
        ),
        encoding="utf-8",
    )
    (bundle / "extracted.md").write_text(
        "\n".join(extracted_parts).strip() + "\n", encoding="utf-8"
    )
    write_source_bundle_manifest(bundle)

    class _FrozenChat:
        def invoke(self, _messages: object) -> SimpleNamespace:
            return SimpleNamespace(content=json.dumps(irene["05B"]), usage_metadata=None)

    def _bomb(*_args: object, **_kwargs: object) -> object:
        raise AssertionError("downstream/provider seam must not be reached")

    monkeypatch.setattr(package_builders, "run_builder_node", _bomb)
    monkeypatch.setattr(workbook_wiring, "run_workbook_band_node", _bomb)
    monkeypatch.setattr(socket, "create_connection", _bomb)
    sim_run_id = "amendment-5-frozen-regression"
    state = RunState(
        graph_version="v0.1-stub",
        temperature=0.0,
        cache_state=CacheState(
            cache_prefix=json.dumps(
                {
                    "mode": "pass-1",
                    "run_id": sim_run_id,
                    "runs_root": str(tmp_path),
                    "bundle_reference": str(bundle),
                    "upstream_output": {"lesson_plan": irene["04A"]},
                    "prior_plan_authority_receipt": prior_receipt,
                },
                sort_keys=True,
            ),
            entries_count=0,
        ),
    )

    with pytest.raises(pass1_act.Pass1AuthorityError) as excinfo:
        pass1_act.act(
            state,
            handle=SimpleNamespace(chat=_FrozenChat()),
            model_id="offline-frozen-regression",
        )

    assert excinfo.value.tag == "irene-pass1.authority-invalid"
    sim_dir = tmp_path / sim_run_id
    forbidden = (
        "irene-pass1.md",
        "irene-pass1.lesson-plan.json",
        "irene-pass1.plan-authority.json",
        "workbook-slide-authority-map.v1.json",
        "workbook-deep-dive-call.v1.json",
        "workbook-brief.v1.json",
        "ask-a-research-call.v1.json",
    )
    assert all(not (sim_dir / name).exists() for name in forbidden)
    after = {
        path.relative_to(copied).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in copied.rglob("*")
        if path.is_file()
    }
    assert after == before
    assert len(after) == 67
