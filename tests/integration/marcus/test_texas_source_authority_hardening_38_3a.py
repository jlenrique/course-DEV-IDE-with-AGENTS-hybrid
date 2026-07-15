from __future__ import annotations

import base64
import hashlib
import importlib.util
import json
import os
import sys
from pathlib import Path

import pytest
import yaml

from app.specialists.source_bundle import (
    SourceBundleError,
    extracted_section_digest,
    parse_extracted_primary_sections,
    read_extracted_source_sections,
    scan_markdown_lines,
)
from app.specialists.texas._act import (
    BundleParseError,
    _anchor_extracted_claims,
    _exclusive_hardening_lock,
    _harden_bundle,
    _publish_transaction_marker,
    _remove_orphaned_staging_files,
    _stage_bytes,
    load_bundle_outputs,
)

RUNNER_PATH = (
    Path(__file__).resolve().parents[3]
    / "skills"
    / "bmad-agent-texas"
    / "scripts"
    / "run_wrangler.py"
)


def _runner_module():
    spec = importlib.util.spec_from_file_location(
        "texas_run_wrangler_38_3a_hardening", RUNNER_PATH
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _write_live_shaped_corpus(tmp_path: Path) -> tuple[Path, Path]:
    course = tmp_path / "course"
    (course / "assessments").mkdir(parents=True)
    (course / "slides").mkdir()
    sources: list[dict[str, object]] = []
    for index in range(1, 6):
        locator = f"assessments/support-{index}.md"
        (course / locator).write_text(
            f"# Support {index}\n\nSupporting context remains separate from slides.\n",
            encoding="utf-8",
        )
        sources.append(
            {
                "ref_id": f"src-{index:03d}",
                "provider": "local_file",
                "locator": locator,
                "role": "supporting",
                "description": f"support {index}",
                "expected_min_words": 1,
            }
        )
    for slide in range(1, 7):
        source_index = slide + 5
        locator = f"slides/slide-{slide}-topic-{slide}.md"
        (course / locator).write_text(
            f"# Slide {slide}\n\n"
            f"- Claim {slide} has enough words to receive an evidence marker.\n"
            f"- Narration {slide} preserves exact source language for planning.\n",
            encoding="utf-8",
        )
        sources.append(
            {
                "ref_id": f"src-{source_index:03d}",
                "provider": "local_file",
                "locator": locator,
                "role": "primary",
                "description": f"slide {slide}",
                "expected_min_words": 1,
            }
        )
    directive = course / "directive.yaml"
    directive.write_text(
        yaml.safe_dump(
            {
                "run_id": "38-3a-live-shaped",
                "corpus_dir": str(course),
                "sources": sources,
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    return course, directive


def _manifest_hashes(bundle: Path) -> dict[str, str]:
    manifest = json.loads((bundle / "manifest.json").read_text(encoding="utf-8"))
    return {row["path"]: row["sha256"] for row in manifest["artifacts"]}


def _reseal_existing_manifest(bundle: Path) -> None:
    manifest_path = bundle / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for row in manifest["artifacts"]:
        raw = (bundle / row["path"]).read_bytes()
        row["sha256"] = hashlib.sha256(raw).hexdigest()
        row["size_bytes"] = len(raw)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def _accept_current_section_bodies(bundle: Path) -> None:
    """Refresh producer-owned projection digests for a deliberate test mutation."""
    metadata_path = bundle / "metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    text = (bundle / "extracted.md").read_text(encoding="utf-8")
    digests = {
        section.source_id: extracted_section_digest(section.body)
        for section in parse_extracted_primary_sections(metadata=metadata, text=text)
    }
    for row in metadata["provenance"]:
        source_id = row.get("ref_id")
        if source_id in digests:
            row["extracted_content_digest"] = digests[source_id]
    for row in metadata["source_authority"]:
        source_id = row.get("source_id")
        if source_id in digests:
            row["extracted_content_digest"] = digests[source_id]
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")


def test_hardening_seals_final_primary_sections_with_owned_evidence(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    course, directive = _write_live_shaped_corpus(tmp_path)
    bundle = tmp_path / "bundle"
    monkeypatch.chdir(course)
    _runner_module().run(directive, bundle)
    before_metadata = json.loads((bundle / "metadata.json").read_text(encoding="utf-8"))
    before_supporting = before_metadata["source_authority"][:5]
    before_source_digests = {
        row["source_id"]: row["source_content_digest"]
        for row in before_metadata["source_authority"]
    }

    _harden_bundle(bundle, directive)

    sections = read_extracted_source_sections({"bundle_reference": str(bundle)})
    assert len(sections) == 6
    for slide, section in enumerate(sections, start=1):
        owned_id = f"src-{slide + 5:03d}"
        assert f"[evidence: {owned_id}]" in section.body
        assert "[evidence: src-001]" not in section.body

    after_metadata = json.loads((bundle / "metadata.json").read_text(encoding="utf-8"))
    assert after_metadata["source_authority"][:5] == before_supporting
    assert {
        row["source_id"]: row["source_content_digest"]
        for row in after_metadata["source_authority"]
    } == before_source_digests
    hashes = _manifest_hashes(bundle)
    for name in ("extracted.md", "metadata.json"):
        assert hashes[name] == hashlib.sha256((bundle / name).read_bytes()).hexdigest()

    first = {
        name: (bundle / name).read_bytes()
        for name in ("extracted.md", "metadata.json", "manifest.json")
    }
    _harden_bundle(bundle, directive)
    assert {
        name: (bundle / name).read_bytes()
        for name in ("extracted.md", "metadata.json", "manifest.json")
    } == first


def test_hardening_rejects_foreign_existing_evidence_marker(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    course, directive = _write_live_shaped_corpus(tmp_path)
    bundle = tmp_path / "bundle"
    monkeypatch.chdir(course)
    _runner_module().run(directive, bundle)
    extracted = bundle / "extracted.md"
    extracted.write_text(
        extracted.read_text(encoding="utf-8").replace(
            "Claim 1 has enough words to receive an evidence marker.",
            "Claim 1 has enough words to receive an evidence marker. [evidence: src-001]",
            1,
        ),
        encoding="utf-8",
    )

    with pytest.raises(BundleParseError):
        _harden_bundle(bundle, directive)


def test_hardening_withdraws_manifest_before_failed_publication(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    course, directive = _write_live_shaped_corpus(tmp_path)
    bundle = tmp_path / "bundle"
    monkeypatch.chdir(course)
    _runner_module().run(directive, bundle)

    calls = 0

    def fail_after_manifest_withdrawal(_path: Path) -> None:
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("durability unavailable")

    monkeypatch.setattr(
        "app.specialists.texas._act._fsync_directory", fail_after_manifest_withdrawal
    )
    with pytest.raises(BundleParseError, match="coherent hardened source bundle"):
        _harden_bundle(bundle, directive)
    assert not (bundle / "manifest.json").exists()
    assert (bundle / ".texas-hardening-transaction.json").exists()

    monkeypatch.undo()
    _harden_bundle(bundle, directive)
    assert (bundle / "manifest.json").exists()
    assert not (bundle / ".texas-hardening-transaction.json").exists()
    assert len(read_extracted_source_sections({"bundle_reference": str(bundle)})) == 6


def test_hardening_rejects_duplicate_metadata_keys_before_mutation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    course, directive = _write_live_shaped_corpus(tmp_path)
    bundle = tmp_path / "bundle"
    monkeypatch.chdir(course)
    _runner_module().run(directive, bundle)
    metadata = bundle / "metadata.json"
    original_extracted = (bundle / "extracted.md").read_bytes()
    metadata.write_text(
        metadata.read_text(encoding="utf-8").replace(
            '"generated_at":', '"generated_at": "duplicate",\n  "generated_at":', 1
        ),
        encoding="utf-8",
    )
    _reseal_existing_manifest(bundle)

    with pytest.raises(BundleParseError, match="malformed"):
        _harden_bundle(bundle, directive)
    assert (bundle / "extracted.md").read_bytes() == original_extracted
    assert (bundle / "manifest.json").exists()


def test_hardening_rejects_hard_linked_authority_coordinate(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    course, directive = _write_live_shaped_corpus(tmp_path)
    bundle = tmp_path / "bundle"
    monkeypatch.chdir(course)
    _runner_module().run(directive, bundle)
    os.link(bundle / "metadata.json", bundle / "metadata-alias.json")

    with pytest.raises(BundleParseError, match="unsafe"):
        _harden_bundle(bundle, directive)
    assert (bundle / "manifest.json").exists()


def test_consumer_rejects_manifest_withdrawn_bundle(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    course, directive = _write_live_shaped_corpus(tmp_path)
    bundle = tmp_path / "bundle"
    monkeypatch.chdir(course)
    _runner_module().run(directive, bundle)
    _harden_bundle(bundle, directive)
    (bundle / "manifest.json").unlink()

    with pytest.raises(SourceBundleError, match="manifest"):
        read_extracted_source_sections({"bundle_reference": str(bundle)})


def test_final_manifest_flush_failure_withdraws_marker_and_recovers(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    course, directive = _write_live_shaped_corpus(tmp_path)
    bundle = tmp_path / "bundle"
    monkeypatch.chdir(course)
    _runner_module().run(directive, bundle)
    from app.specialists.texas import _act as texas_act

    real_flush = texas_act._fsync_directory
    calls = 0

    def fail_final_manifest_flush(path: Path) -> None:
        nonlocal calls
        calls += 1
        if calls == 4:
            raise OSError("final manifest durability unavailable")
        real_flush(path)

    monkeypatch.setattr(texas_act, "_fsync_directory", fail_final_manifest_flush)
    with pytest.raises(BundleParseError, match="hardened manifest"):
        _harden_bundle(bundle, directive)
    assert not (bundle / "manifest.json").exists()
    assert (bundle / ".texas-hardening-transaction.json").exists()

    monkeypatch.setattr(texas_act, "_fsync_directory", real_flush)
    _harden_bundle(bundle, directive)
    assert (bundle / "manifest.json").is_file()
    assert not (bundle / ".texas-hardening-transaction.json").exists()


@pytest.mark.parametrize(
    ("field", "value"),
    [("ref_id", "src] forged"), ("ref", "slides/../slides/slide-1-topic-1.md")],
)
def test_hardening_rejects_unsafe_primary_identity_or_path(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    field: str,
    value: str,
) -> None:
    course, directive = _write_live_shaped_corpus(tmp_path)
    bundle = tmp_path / "bundle"
    monkeypatch.chdir(course)
    _runner_module().run(directive, bundle)
    metadata_path = bundle / "metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    metadata["provenance"][5][field] = value
    if field == "ref_id":
        metadata["source_authority"][5]["source_id"] = value
    else:
        metadata["source_authority"][5]["path"] = value
    metadata_path.write_text(json.dumps(metadata), encoding="utf-8")
    _reseal_existing_manifest(bundle)

    with pytest.raises(BundleParseError):
        _harden_bundle(bundle, directive)


def test_hardening_rejects_marker_variant_and_preserves_literal_blocks(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    course, directive = _write_live_shaped_corpus(tmp_path)
    bundle = tmp_path / "bundle"
    monkeypatch.chdir(course)
    _runner_module().run(directive, bundle)
    extracted = bundle / "extracted.md"
    extracted.write_text(
        extracted.read_text(encoding="utf-8").replace(
            "Claim 1 has enough words to receive an evidence marker.",
            "Claim 1 has enough words. [ Evidence : src-006]",
            1,
        ),
        encoding="utf-8",
    )
    _accept_current_section_bodies(bundle)
    _reseal_existing_manifest(bundle)
    with pytest.raises(BundleParseError, match="foreign or ambiguous"):
        _harden_bundle(bundle, directive)

    _runner_module().run(directive, bundle)
    extracted.write_text(
        extracted.read_text(encoding="utf-8").replace(
            "- Claim 1 has enough words to receive an evidence marker.",
            "```text\n[evidence: literal-example]\n```\n"
            "- Claim 1 has enough words to receive an evidence marker.",
            1,
        ),
        encoding="utf-8",
    )
    _accept_current_section_bodies(bundle)
    _reseal_existing_manifest(bundle)
    _harden_bundle(bundle, directive)
    hardened = extracted.read_text(encoding="utf-8")
    assert "[evidence: literal-example]\n```" in hardened
    assert "[evidence: literal-example] [evidence:" not in hardened


def test_hardening_requires_claim_in_every_primary_section(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    course, directive = _write_live_shaped_corpus(tmp_path)
    bundle = tmp_path / "bundle"
    monkeypatch.chdir(course)
    _runner_module().run(directive, bundle)
    extracted = bundle / "extracted.md"
    text = extracted.read_text(encoding="utf-8")
    metadata = json.loads((bundle / "metadata.json").read_text(encoding="utf-8"))
    first_title = metadata["provenance"][5]["section_title"]
    second_title = metadata["provenance"][6]["section_title"]
    start = text.index(f"## {first_title}")
    end = text.index(f"## {second_title}")
    extracted.write_text(
        text[:start] + f"## {first_title}\n\n# Heading only\n\n" + text[end:],
        encoding="utf-8",
    )
    _accept_current_section_bodies(bundle)
    _reseal_existing_manifest(bundle)

    with pytest.raises(BundleParseError, match="anchorable claim"):
        _harden_bundle(bundle, directive)


def test_hardening_rejects_duplicate_yaml_keys(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    course, directive = _write_live_shaped_corpus(tmp_path)
    bundle = tmp_path / "bundle"
    monkeypatch.chdir(course)
    _runner_module().run(directive, bundle)
    directive.write_text(
        directive.read_text(encoding="utf-8") + "run_id: duplicate\n",
        encoding="utf-8",
    )
    with pytest.raises(BundleParseError, match="cannot be loaded"):
        _harden_bundle(bundle, directive)


@pytest.mark.parametrize("name", ["extraction-report.yaml", "result.yaml"])
def test_hardening_rejects_duplicate_bundle_yaml_keys(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    name: str,
) -> None:
    course, directive = _write_live_shaped_corpus(tmp_path)
    bundle = tmp_path / "bundle"
    monkeypatch.chdir(course)
    _runner_module().run(directive, bundle)
    path = bundle / name
    path.write_text(
        path.read_text(encoding="utf-8") + "run_id: duplicate\n",
        encoding="utf-8",
    )
    _reseal_existing_manifest(bundle)

    with pytest.raises(BundleParseError, match="invalid|malformed"):
        _harden_bundle(bundle, directive)


def test_consumer_validates_non_slide_primary_digest_before_filtering(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    course, directive = _write_live_shaped_corpus(tmp_path)
    bundle = tmp_path / "bundle"
    monkeypatch.chdir(course)
    _runner_module().run(directive, bundle)
    _harden_bundle(bundle, directive)
    metadata_path = bundle / "metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    metadata["provenance"][5]["ref"] = "notes/non-slide.md"
    metadata["source_authority"][5]["path"] = "notes/non-slide.md"
    metadata["source_authority"][5]["extracted_content_digest"] = "0" * 64
    metadata_path.write_text(json.dumps(metadata), encoding="utf-8")
    _reseal_existing_manifest(bundle)

    with pytest.raises(SourceBundleError, match="disagrees"):
        read_extracted_source_sections({"bundle_reference": str(bundle)})


@pytest.mark.parametrize("field", ["status", "materials"])
def test_hardening_rejects_tampered_result_fields(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, field: str
) -> None:
    course, directive = _write_live_shaped_corpus(tmp_path)
    bundle = tmp_path / "bundle"
    monkeypatch.chdir(course)
    _runner_module().run(directive, bundle)
    result_path = bundle / "result.yaml"
    result = yaml.safe_load(result_path.read_text(encoding="utf-8"))
    result[field] = "forged"
    result_path.write_text(yaml.safe_dump(result), encoding="utf-8")

    with pytest.raises(BundleParseError, match="does not authenticate result.yaml"):
        _harden_bundle(bundle, directive)


def test_consumer_rejects_visible_manifest_while_transaction_exists(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    course, directive = _write_live_shaped_corpus(tmp_path)
    bundle = tmp_path / "bundle"
    monkeypatch.chdir(course)
    _runner_module().run(directive, bundle)
    _harden_bundle(bundle, directive)
    (bundle / ".texas-hardening-transaction.json").write_text(
        "publication incomplete\n", encoding="utf-8"
    )

    with pytest.raises(SourceBundleError, match="transaction"):
        read_extracted_source_sections({"bundle_reference": str(bundle)})


@pytest.mark.parametrize(
    ("kind", "ref"),
    [
        ("local_file", "C:/slides/slide-1-topic-1.md"),
        ("unknown-provider", "slides/slide-1-topic-1.md"),
    ],
)
def test_hardening_rejects_drive_qualified_or_unknown_primary_coordinates(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    kind: str,
    ref: str,
) -> None:
    course, directive = _write_live_shaped_corpus(tmp_path)
    bundle = tmp_path / "bundle"
    monkeypatch.chdir(course)
    _runner_module().run(directive, bundle)
    metadata_path = bundle / "metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    metadata["provenance"][5]["kind"] = kind
    metadata["provenance"][5]["ref"] = ref
    metadata["source_authority"][5]["path"] = ref
    metadata_path.write_text(json.dumps(metadata), encoding="utf-8")
    _reseal_existing_manifest(bundle)

    with pytest.raises(BundleParseError):
        _harden_bundle(bundle, directive)


def test_nested_fences_do_not_create_boundaries_or_anchor_literal_examples(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    course, directive = _write_live_shaped_corpus(tmp_path)
    bundle = tmp_path / "bundle"
    monkeypatch.chdir(course)
    _runner_module().run(directive, bundle)
    extracted = bundle / "extracted.md"
    metadata = json.loads((bundle / "metadata.json").read_text(encoding="utf-8"))
    second_title = metadata["provenance"][6]["section_title"]
    text = extracted.read_text(encoding="utf-8").replace(
        "- Claim 1 has enough words to receive an evidence marker.",
        "````markdown\n```\n"
        f"## {second_title}\n"
        "[evidence: literal-example]\n```\n````\n"
        "- Claim 1 has enough words to receive an evidence marker.",
        1,
    )
    extracted.write_text(text, encoding="utf-8")
    _accept_current_section_bodies(bundle)
    _reseal_existing_manifest(bundle)

    _harden_bundle(bundle, directive)
    hardened = extracted.read_text(encoding="utf-8")
    assert "[evidence: literal-example]\n```\n````" in hardened
    assert "[evidence: literal-example] [evidence:" not in hardened


def test_table_foreign_marker_is_rejected_even_though_table_is_not_a_claim(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    course, directive = _write_live_shaped_corpus(tmp_path)
    bundle = tmp_path / "bundle"
    monkeypatch.chdir(course)
    _runner_module().run(directive, bundle)
    extracted = bundle / "extracted.md"
    extracted.write_text(
        extracted.read_text(encoding="utf-8").replace(
            "- Claim 1 has enough words to receive an evidence marker.",
            "| claim | source |\n| --- | --- |\n"
            "| enough context | [evidence: src-001] |\n"
            "- Claim 1 has enough words to receive an evidence marker.",
            1,
        ),
        encoding="utf-8",
    )
    _accept_current_section_bodies(bundle)
    _reseal_existing_manifest(bundle)

    with pytest.raises(BundleParseError, match="foreign or ambiguous"):
        _harden_bundle(bundle, directive)


def test_structural_only_primary_section_does_not_satisfy_claim_floor(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    course, directive = _write_live_shaped_corpus(tmp_path)
    bundle = tmp_path / "bundle"
    monkeypatch.chdir(course)
    _runner_module().run(directive, bundle)
    extracted = bundle / "extracted.md"
    text = extracted.read_text(encoding="utf-8")
    metadata = json.loads((bundle / "metadata.json").read_text(encoding="utf-8"))
    first_title = metadata["provenance"][5]["section_title"]
    second_title = metadata["provenance"][6]["section_title"]
    start = text.index(f"## {first_title}")
    end = text.index(f"## {second_title}")
    structural = (
        f"## {first_title}\n\n"
        "[reference]: https://example.test\n"
        "![diagram](diagram.png)\n"
        "[link only](https://example.test)\n"
        "https://example.test\n"
            "<span>\n</span>\n\n"
        "| heading | value |\n| --- | --- |\n| one | two |\n"
    )
    extracted.write_text(text[:start] + structural + text[end:], encoding="utf-8")
    _accept_current_section_bodies(bundle)
    _reseal_existing_manifest(bundle)

    with pytest.raises(BundleParseError, match="anchorable claim"):
        _harden_bundle(bundle, directive)


def test_hardening_lock_rejects_a_second_publisher(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    with (
        _exclusive_hardening_lock(bundle),
        pytest.raises(BundleParseError, match="already active"),
        _exclusive_hardening_lock(bundle),
    ):
        pytest.fail("a second publisher acquired the hardening lock")


def test_stage_chmod_failure_leaves_no_temporary_artifact(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = tmp_path / "metadata.json"

    def fail_chmod(_path: Path, _mode: int) -> None:
        raise OSError("permission hardening unavailable")

    monkeypatch.setattr(os, "chmod", fail_chmod)
    with pytest.raises(BundleParseError, match="cannot stage"):
        _stage_bytes(target, b"payload")
    assert list(tmp_path.iterdir()) == []


def test_all_original_recovery_ignores_incomplete_unused_target_set(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    course, directive = _write_live_shaped_corpus(tmp_path)
    bundle = tmp_path / "bundle"
    monkeypatch.chdir(course)
    _runner_module().run(directive, bundle)
    from app.specialists.texas import _act as texas_act

    real_flush = texas_act._fsync_directory
    calls = 0

    def fail_after_manifest_withdrawal(path: Path) -> None:
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("stop after manifest withdrawal")
        real_flush(path)

    monkeypatch.setattr(texas_act, "_fsync_directory", fail_after_manifest_withdrawal)
    with pytest.raises(BundleParseError):
        _harden_bundle(bundle, directive)
    marker = bundle / ".texas-hardening-transaction.json"
    transaction = json.loads(marker.read_text(encoding="utf-8"))
    del transaction["targets"]["result.yaml"]
    marker.write_text(json.dumps(transaction), encoding="utf-8")
    monkeypatch.setattr(texas_act, "_fsync_directory", real_flush)

    _harden_bundle(bundle, directive)
    assert not marker.exists()
    assert (bundle / "manifest.json").exists()


def test_recovery_ignores_semantically_forged_transaction_target(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    course, directive = _write_live_shaped_corpus(tmp_path)
    bundle = tmp_path / "bundle"
    monkeypatch.chdir(course)
    _runner_module().run(directive, bundle)
    from app.specialists.texas import _act as texas_act

    real_flush = texas_act._fsync_directory
    calls = 0

    def fail_after_manifest_withdrawal(path: Path) -> None:
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("stop after manifest withdrawal")
        real_flush(path)

    monkeypatch.setattr(texas_act, "_fsync_directory", fail_after_manifest_withdrawal)
    with pytest.raises(BundleParseError):
        _harden_bundle(bundle, directive)
    marker = bundle / ".texas-hardening-transaction.json"
    transaction = json.loads(marker.read_text(encoding="utf-8"))
    forged = b"run_id: 38-3a-live-shaped\nstatus: forged\n"
    transaction["targets"]["result.yaml"] = {
        "sha256": hashlib.sha256(forged).hexdigest(),
        "payload_b64": base64.b64encode(forged).decode("ascii"),
    }
    marker.write_text(json.dumps(transaction), encoding="utf-8")
    monkeypatch.setattr(texas_act, "_fsync_directory", real_flush)

    _harden_bundle(bundle, directive)
    assert not marker.exists()
    assert (bundle / "manifest.json").exists()
    recovered_result = yaml.safe_load(
        (bundle / "result.yaml").read_text(encoding="utf-8")
    )
    recovered_report = yaml.safe_load(
        (bundle / "extraction-report.yaml").read_text(encoding="utf-8")
    )
    assert recovered_result["status"] != "forged"
    assert recovered_result["status"] == recovered_report["overall_status"]


def test_manifest_flush_and_withdrawal_failure_remains_invisible_to_consumers(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    course, directive = _write_live_shaped_corpus(tmp_path)
    bundle = tmp_path / "bundle"
    monkeypatch.chdir(course)
    _runner_module().run(directive, bundle)
    from app.specialists.texas import _act as texas_act

    real_flush = texas_act._fsync_directory
    real_unlink = Path.unlink
    calls = 0

    def fail_final_manifest_flush(path: Path) -> None:
        nonlocal calls
        calls += 1
        if calls == 4:
            raise OSError("final manifest durability unavailable")
        real_flush(path)

    def fail_manifest_withdrawal(path: Path, *args, **kwargs) -> None:
        if path == bundle / "manifest.json" and calls >= 4:
            raise OSError("manifest withdrawal unavailable")
        real_unlink(path, *args, **kwargs)

    monkeypatch.setattr(texas_act, "_fsync_directory", fail_final_manifest_flush)
    monkeypatch.setattr(Path, "unlink", fail_manifest_withdrawal)
    with pytest.raises(BundleParseError, match="hardened manifest"):
        _harden_bundle(bundle, directive)
    assert (bundle / "manifest.json").exists()
    assert (bundle / ".texas-hardening-transaction.json").exists()
    with pytest.raises(SourceBundleError, match="transaction"):
        read_extracted_source_sections({"bundle_reference": str(bundle)})

    monkeypatch.setattr(texas_act, "_fsync_directory", real_flush)
    monkeypatch.setattr(Path, "unlink", real_unlink)
    _harden_bundle(bundle, directive)
    assert not (bundle / ".texas-hardening-transaction.json").exists()


def test_ordinary_pipe_prose_is_anchored_as_a_claim(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    course, directive = _write_live_shaped_corpus(tmp_path)
    bundle = tmp_path / "bundle"
    monkeypatch.chdir(course)
    _runner_module().run(directive, bundle)
    extracted = bundle / "extracted.md"
    extracted.write_text(
        extracted.read_text(encoding="utf-8").replace(
            "Claim 1 has enough words to receive an evidence marker.",
            "Use A | B to compare the available options clearly.",
            1,
        ),
        encoding="utf-8",
    )
    _accept_current_section_bodies(bundle)
    _reseal_existing_manifest(bundle)

    _harden_bundle(bundle, directive)
    assert "Use A | B to compare the available options clearly. [evidence: src-006]" in (
        extracted.read_text(encoding="utf-8")
    )


def test_slide_primary_requires_explicit_local_kind(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    course, directive = _write_live_shaped_corpus(tmp_path)
    bundle = tmp_path / "bundle"
    monkeypatch.chdir(course)
    _runner_module().run(directive, bundle)
    metadata_path = bundle / "metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    del metadata["provenance"][5]["kind"]
    metadata_path.write_text(json.dumps(metadata), encoding="utf-8")
    _reseal_existing_manifest(bundle)

    with pytest.raises(BundleParseError):
        _harden_bundle(bundle, directive)


def test_missing_primary_authority_row_is_recoverably_classified(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    course, directive = _write_live_shaped_corpus(tmp_path)
    bundle = tmp_path / "bundle"
    monkeypatch.chdir(course)
    _runner_module().run(directive, bundle)
    metadata_path = bundle / "metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    metadata["provenance"][5]["kind"] = "url"
    metadata["provenance"][5]["ref"] = "https://example.test/source"
    del metadata["source_authority"][5]
    metadata_path.write_text(json.dumps(metadata), encoding="utf-8")
    _reseal_existing_manifest(bundle)

    with pytest.raises(SourceBundleError):
        read_extracted_source_sections({"bundle_reference": str(bundle)})


def test_partial_transaction_marker_is_removed_when_publication_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    marker = tmp_path / ".texas-hardening-transaction.json"

    def fail_fsync(_descriptor: int) -> None:
        raise OSError("file durability unavailable")

    monkeypatch.setattr(os, "fsync", fail_fsync)
    with pytest.raises(BundleParseError, match="exclusively acquire"):
        _publish_transaction_marker(marker, b"partial")
    assert not marker.exists()


def test_html_block_heading_text_is_not_a_primary_boundary(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    course, directive = _write_live_shaped_corpus(tmp_path)
    bundle = tmp_path / "bundle"
    monkeypatch.chdir(course)
    _runner_module().run(directive, bundle)
    extracted = bundle / "extracted.md"
    metadata = json.loads((bundle / "metadata.json").read_text(encoding="utf-8"))
    second_title = metadata["provenance"][6]["section_title"]
    extracted.write_text(
        extracted.read_text(encoding="utf-8").replace(
            "- Claim 1 has enough words to receive an evidence marker.",
            f"<div>\n## {second_title}\n</div>\n\n"
            "- Claim 1 has enough words to receive an evidence marker.",
            1,
        ),
        encoding="utf-8",
    )
    _accept_current_section_bodies(bundle)
    _reseal_existing_manifest(bundle)
    _harden_bundle(bundle, directive)


def test_inline_code_evidence_example_is_preserved_as_literal(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    course, directive = _write_live_shaped_corpus(tmp_path)
    bundle = tmp_path / "bundle"
    monkeypatch.chdir(course)
    _runner_module().run(directive, bundle)
    extracted = bundle / "extracted.md"
    extracted.write_text(
        extracted.read_text(encoding="utf-8").replace(
            "Claim 1 has enough words to receive an evidence marker.",
            "Use `[evidence: example]` when documenting the syntax.",
            1,
        ),
        encoding="utf-8",
    )
    _accept_current_section_bodies(bundle)
    _reseal_existing_manifest(bundle)
    _harden_bundle(bundle, directive)
    assert (
        "Use `[evidence: example]` when documenting the syntax. "
        "[evidence: src-006]"
    ) in extracted.read_text(encoding="utf-8")


def test_setext_heading_is_preserved_and_not_counted_as_claim(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    course, directive = _write_live_shaped_corpus(tmp_path)
    bundle = tmp_path / "bundle"
    monkeypatch.chdir(course)
    _runner_module().run(directive, bundle)
    extracted = bundle / "extracted.md"
    extracted.write_text(
        extracted.read_text(encoding="utf-8").replace(
            "- Claim 1 has enough words to receive an evidence marker.",
            "Structural subheading\n---\n"
            "- Claim 1 has enough words to receive an evidence marker.",
            1,
        ),
        encoding="utf-8",
    )
    _accept_current_section_bodies(bundle)
    _reseal_existing_manifest(bundle)
    _harden_bundle(bundle, directive)
    hardened = extracted.read_text(encoding="utf-8")
    assert "Structural subheading\n---" in hardened
    assert "Structural subheading [evidence:" not in hardened


def test_manifest_read_failure_uses_manifest_diagnostic_tag(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    course, directive = _write_live_shaped_corpus(tmp_path)
    bundle = tmp_path / "bundle"
    monkeypatch.chdir(course)
    _runner_module().run(directive, bundle)
    (bundle / "manifest.json").unlink()

    with pytest.raises(SourceBundleError) as failure:
        read_extracted_source_sections({"bundle_reference": str(bundle)})
    assert failure.value.tag == "source.bundle.manifest-invalid"


def test_orphaned_unique_staging_files_are_removed_under_lock(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    orphan = bundle / ".metadata.json.texas-hardening-crash.tmp"
    orphan.write_text("residue", encoding="utf-8")
    _remove_orphaned_staging_files(bundle)
    assert not orphan.exists()


def test_recovery_recomputes_from_original_instead_of_trusting_target_claims(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    course, directive = _write_live_shaped_corpus(tmp_path)
    bundle = tmp_path / "bundle"
    monkeypatch.chdir(course)
    _runner_module().run(directive, bundle)
    from app.specialists.texas import _act as texas_act

    real_flush = texas_act._fsync_directory
    calls = 0

    def fail_after_manifest_withdrawal(path: Path) -> None:
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("stop after manifest withdrawal")
        real_flush(path)

    monkeypatch.setattr(texas_act, "_fsync_directory", fail_after_manifest_withdrawal)
    with pytest.raises(BundleParseError):
        _harden_bundle(bundle, directive)
    marker = bundle / ".texas-hardening-transaction.json"
    transaction = json.loads(marker.read_text(encoding="utf-8"))
    target_rows = transaction["targets"]
    forged_extracted = base64.b64decode(
        target_rows["extracted.md"]["payload_b64"]
    ).replace(b"[evidence: src-006]", b"[evidence: src-001]", 1)
    metadata = json.loads(
        base64.b64decode(target_rows["metadata.json"]["payload_b64"])
    )
    sections = parse_extracted_primary_sections(
        metadata=metadata, text=forged_extracted.decode("utf-8")
    )
    digest_by_id = {
        section.source_id: extracted_section_digest(section.body)
        for section in sections
    }
    for row in metadata["source_authority"]:
        if row["source_id"] in digest_by_id:
            row["extracted_content_digest"] = digest_by_id[row["source_id"]]
    forged_metadata = (json.dumps(metadata, indent=2) + "\n").encode("utf-8")
    for name, payload in (
        ("extracted.md", forged_extracted),
        ("metadata.json", forged_metadata),
    ):
        target_rows[name] = {
            "sha256": hashlib.sha256(payload).hexdigest(),
            "payload_b64": base64.b64encode(payload).decode("ascii"),
        }
    marker.write_text(json.dumps(transaction), encoding="utf-8")
    monkeypatch.setattr(texas_act, "_fsync_directory", real_flush)

    _harden_bundle(bundle, directive)
    assert not marker.exists()
    assert (bundle / "manifest.json").exists()
    hardened = (bundle / "extracted.md").read_text(encoding="utf-8")
    assert "[evidence: src-001]" not in hardened
    assert "[evidence: src-006]" in hardened


def test_atx_heading_preserves_unspaced_literal_hash() -> None:
    heading = scan_markdown_lines("## C#\n")[0]
    assert heading.heading_level == 2
    assert heading.heading_text == "C#"


def test_unclosed_and_self_closing_html_blocks_do_not_hide_later_boundaries(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    course, directive = _write_live_shaped_corpus(tmp_path)
    bundle = tmp_path / "bundle"
    monkeypatch.chdir(course)
    _runner_module().run(directive, bundle)
    extracted = bundle / "extracted.md"
    extracted.write_text(
        extracted.read_text(encoding="utf-8").replace(
            "- Claim 1 has enough words to receive an evidence marker.",
            "<div>\nHTML example\n\n"
                "<hr />\n\n"
            "- Claim 1 has enough words to receive an evidence marker.",
            1,
        ),
        encoding="utf-8",
    )
    _accept_current_section_bodies(bundle)
    _reseal_existing_manifest(bundle)
    _harden_bundle(bundle, directive)
    assert len(read_extracted_source_sections({"bundle_reference": str(bundle)})) == 6


def test_unequal_backtick_runs_do_not_hide_foreign_evidence(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    course, directive = _write_live_shaped_corpus(tmp_path)
    bundle = tmp_path / "bundle"
    monkeypatch.chdir(course)
    _runner_module().run(directive, bundle)
    extracted = bundle / "extracted.md"
    extracted.write_text(
        extracted.read_text(encoding="utf-8").replace(
            "Claim 1 has enough words to receive an evidence marker.",
            "Use ``[evidence: src-001]``` in malformed prose.",
            1,
        ),
        encoding="utf-8",
    )
    _accept_current_section_bodies(bundle)
    _reseal_existing_manifest(bundle)
    with pytest.raises(BundleParseError, match="foreign or ambiguous"):
        _harden_bundle(bundle, directive)


def test_blockquoted_tables_and_setext_headings_remain_structural(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    course, directive = _write_live_shaped_corpus(tmp_path)
    bundle = tmp_path / "bundle"
    monkeypatch.chdir(course)
    _runner_module().run(directive, bundle)
    extracted = bundle / "extracted.md"
    extracted.write_text(
        extracted.read_text(encoding="utf-8").replace(
            "- Claim 1 has enough words to receive an evidence marker.",
            "> Structural heading\n> ---\n"
            "> | column | value |\n> | --- | --- |\n> | one | two |\n"
            "- Claim 1 has enough words to receive an evidence marker.",
            1,
        ),
        encoding="utf-8",
    )
    _accept_current_section_bodies(bundle)
    _reseal_existing_manifest(bundle)
    _harden_bundle(bundle, directive)
    hardened = extracted.read_text(encoding="utf-8")
    assert "> Structural heading\n> ---" in hardened
    assert "> | one | two | [evidence:" not in hardened


def test_local_pdf_primary_requires_matching_path_authority(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    course, directive = _write_live_shaped_corpus(tmp_path)
    bundle = tmp_path / "bundle"
    monkeypatch.chdir(course)
    _runner_module().run(directive, bundle)
    metadata_path = bundle / "metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    metadata["provenance"][5]["kind"] = "pdf"
    metadata["provenance"][5]["ref"] = "documents/source.pdf"
    metadata["source_authority"][5]["path"] = None
    metadata_path.write_text(json.dumps(metadata), encoding="utf-8")
    _reseal_existing_manifest(bundle)
    with pytest.raises(BundleParseError):
        _harden_bundle(bundle, directive)


def test_consumer_rejects_incomplete_manifest_inventory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    course, directive = _write_live_shaped_corpus(tmp_path)
    bundle = tmp_path / "bundle"
    monkeypatch.chdir(course)
    _runner_module().run(directive, bundle)
    manifest_path = bundle / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["artifacts"] = [
        row for row in manifest["artifacts"] if row["path"] != "result.yaml"
    ]
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(SourceBundleError, match="inventory is incomplete"):
        read_extracted_source_sections({"bundle_reference": str(bundle)})


def test_escaped_backticks_do_not_hide_visible_foreign_evidence(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    course, directive = _write_live_shaped_corpus(tmp_path)
    bundle = tmp_path / "bundle"
    monkeypatch.chdir(course)
    _runner_module().run(directive, bundle)
    extracted = bundle / "extracted.md"
    extracted.write_text(
        extracted.read_text(encoding="utf-8").replace(
            "Claim 1 has enough words to receive an evidence marker.",
            r"Use \`[evidence: src-001]\` in visible prose.",
            1,
        ),
        encoding="utf-8",
    )
    _accept_current_section_bodies(bundle)
    _reseal_existing_manifest(bundle)
    with pytest.raises(BundleParseError, match="foreign or ambiguous"):
        _harden_bundle(bundle, directive)


def test_multiline_code_span_preserves_literal_evidence_example(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    course, directive = _write_live_shaped_corpus(tmp_path)
    bundle = tmp_path / "bundle"
    monkeypatch.chdir(course)
    _runner_module().run(directive, bundle)
    extracted = bundle / "extracted.md"
    extracted.write_text(
        extracted.read_text(encoding="utf-8").replace(
            "- Claim 1 has enough words to receive an evidence marker.",
            "- Use `literal syntax\n[evidence: example]` in documentation.\n"
            "- Claim 1 has enough words to receive an evidence marker.",
            1,
        ),
        encoding="utf-8",
    )
    _accept_current_section_bodies(bundle)
    _reseal_existing_manifest(bundle)
    _harden_bundle(bundle, directive)
    hardened = extracted.read_text(encoding="utf-8")
    assert "[evidence: example]`" in hardened
    assert "[evidence: example] [evidence:" not in hardened


def test_remaining_commonmark_html_block_forms_hide_literal_headings(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    course, directive = _write_live_shaped_corpus(tmp_path)
    bundle = tmp_path / "bundle"
    monkeypatch.chdir(course)
    _runner_module().run(directive, bundle)
    extracted = bundle / "extracted.md"
    metadata = json.loads((bundle / "metadata.json").read_text(encoding="utf-8"))
    second_title = metadata["provenance"][6]["section_title"]
    literals = (
        f"<?instruction\n## {second_title}\n?>\n"
        f"<!DECLARATION\n## {second_title}\n>\n"
        f"<![CDATA[\n## {second_title}\n]]>\n"
        f"<custom-widget>\n## {second_title}\n</custom-widget>\n\n"
    )
    extracted.write_text(
        extracted.read_text(encoding="utf-8").replace(
            "- Claim 1 has enough words to receive an evidence marker.",
            literals + "- Claim 1 has enough words to receive an evidence marker.",
            1,
        ),
        encoding="utf-8",
    )
    _accept_current_section_bodies(bundle)
    _reseal_existing_manifest(bundle)
    _harden_bundle(bundle, directive)


def test_consumer_hashes_non_source_artifacts_before_accepting_manifest(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    course, directive = _write_live_shaped_corpus(tmp_path)
    bundle = tmp_path / "bundle"
    monkeypatch.chdir(course)
    _runner_module().run(directive, bundle)
    result_path = bundle / "result.yaml"
    result_path.write_text("forged: true\n", encoding="utf-8")
    with pytest.raises(SourceBundleError, match="does not bind result.yaml"):
        read_extracted_source_sections({"bundle_reference": str(bundle)})


def test_all_original_recovery_ignores_corrupt_unused_targets(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    course, directive = _write_live_shaped_corpus(tmp_path)
    bundle = tmp_path / "bundle"
    monkeypatch.chdir(course)
    _runner_module().run(directive, bundle)
    from app.specialists.texas import _act as texas_act

    real_flush = texas_act._fsync_directory
    calls = 0

    def fail_after_manifest_withdrawal(path: Path) -> None:
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("stop while artifacts remain original")
        real_flush(path)

    monkeypatch.setattr(texas_act, "_fsync_directory", fail_after_manifest_withdrawal)
    with pytest.raises(BundleParseError):
        _harden_bundle(bundle, directive)
    marker = bundle / ".texas-hardening-transaction.json"
    transaction = json.loads(marker.read_text(encoding="utf-8"))
    transaction["targets"]["result.yaml"] = {
        "sha256": "0" * 64,
        "payload_b64": "not-base64",
    }
    marker.write_text(json.dumps(transaction), encoding="utf-8")
    monkeypatch.setattr(texas_act, "_fsync_directory", real_flush)
    _harden_bundle(bundle, directive)
    assert not marker.exists()


def test_multiline_code_only_section_cannot_satisfy_claim_floor(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    course, directive = _write_live_shaped_corpus(tmp_path)
    bundle = tmp_path / "bundle"
    monkeypatch.chdir(course)
    _runner_module().run(directive, bundle)
    extracted = bundle / "extracted.md"
    text = extracted.read_text(encoding="utf-8")
    metadata = json.loads((bundle / "metadata.json").read_text(encoding="utf-8"))
    first_title = metadata["provenance"][5]["section_title"]
    second_title = metadata["provenance"][6]["section_title"]
    start = text.index(f"## {first_title}")
    end = text.index(f"## {second_title}")
    extracted.write_text(
        text[:start] + f"## {first_title}\n\n`literal\nmore literal`\n\n" + text[end:],
        encoding="utf-8",
    )
    _accept_current_section_bodies(bundle)
    _reseal_existing_manifest(bundle)
    with pytest.raises(BundleParseError, match="anchorable claim"):
        _harden_bundle(bundle, directive)


def test_list_contained_fence_hides_literal_heading(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    course, directive = _write_live_shaped_corpus(tmp_path)
    bundle = tmp_path / "bundle"
    monkeypatch.chdir(course)
    _runner_module().run(directive, bundle)
    extracted = bundle / "extracted.md"
    metadata = json.loads((bundle / "metadata.json").read_text(encoding="utf-8"))
    second_title = metadata["provenance"][6]["section_title"]
    extracted.write_text(
        extracted.read_text(encoding="utf-8").replace(
            "- Claim 1 has enough words to receive an evidence marker.",
            f"- ```markdown\n  ## {second_title}\n  ```\n"
            "- Claim 1 has enough words to receive an evidence marker.",
            1,
        ),
        encoding="utf-8",
    )
    _accept_current_section_bodies(bundle)
    _reseal_existing_manifest(bundle)
    _harden_bundle(bundle, directive)


def test_literal_state_ends_when_blockquote_container_ends(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    course, directive = _write_live_shaped_corpus(tmp_path)
    bundle = tmp_path / "bundle"
    monkeypatch.chdir(course)
    _runner_module().run(directive, bundle)
    extracted = bundle / "extracted.md"
    extracted.write_text(
        extracted.read_text(encoding="utf-8").replace(
            "- Claim 1 has enough words to receive an evidence marker.",
            "> ```\n> literal without a closing fence\n"
            "- Claim 1 has enough words to receive an evidence marker.",
            1,
        ),
        encoding="utf-8",
    )
    _accept_current_section_bodies(bundle)
    _reseal_existing_manifest(bundle)
    _harden_bundle(bundle, directive)


def test_type7_html_does_not_interrupt_active_paragraph() -> None:
    lines = scan_markdown_lines("paragraph\n<custom-widget>\n## Boundary\n")
    assert lines[2].heading_level == 2
    assert lines[2].heading_text == "Boundary"


def test_unclosed_list_fence_ends_with_its_list_container(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    course, directive = _write_live_shaped_corpus(tmp_path)
    bundle = tmp_path / "bundle"
    monkeypatch.chdir(course)
    _runner_module().run(directive, bundle)
    extracted = bundle / "extracted.md"
    extracted.write_text(
        extracted.read_text(encoding="utf-8").replace(
            "- Narration 1 preserves exact source language for planning.",
            "- ```\n  literal without closer",
            1,
        ),
        encoding="utf-8",
    )
    _accept_current_section_bodies(bundle)
    _reseal_existing_manifest(bundle)
    _harden_bundle(bundle, directive)
    assert len(read_extracted_source_sections({"bundle_reference": str(bundle)})) == 6


def test_list_contained_html_hides_literal_primary_heading(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    course, directive = _write_live_shaped_corpus(tmp_path)
    bundle = tmp_path / "bundle"
    monkeypatch.chdir(course)
    _runner_module().run(directive, bundle)
    extracted = bundle / "extracted.md"
    metadata = json.loads((bundle / "metadata.json").read_text(encoding="utf-8"))
    second_title = metadata["provenance"][6]["section_title"]
    extracted.write_text(
        extracted.read_text(encoding="utf-8").replace(
            "- Claim 1 has enough words to receive an evidence marker.",
            f"- <div>\n  ## {second_title}\n\n"
            "- Claim 1 has enough words to receive an evidence marker.",
            1,
        ),
        encoding="utf-8",
    )
    _accept_current_section_bodies(bundle)
    _reseal_existing_manifest(bundle)
    _harden_bundle(bundle, directive)


def test_adjacent_multiline_code_spans_cannot_satisfy_claim_floor(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    course, directive = _write_live_shaped_corpus(tmp_path)
    bundle = tmp_path / "bundle"
    monkeypatch.chdir(course)
    _runner_module().run(directive, bundle)
    extracted = bundle / "extracted.md"
    text = extracted.read_text(encoding="utf-8")
    metadata = json.loads((bundle / "metadata.json").read_text(encoding="utf-8"))
    first_title = metadata["provenance"][5]["section_title"]
    second_title = metadata["provenance"][6]["section_title"]
    start = text.index(f"## {first_title}")
    end = text.index(f"## {second_title}")
    extracted.write_text(
        text[:start]
        + f"## {first_title}\n\n`one\nmore` ``two\nmore``\n\n"
        + text[end:],
        encoding="utf-8",
    )
    _accept_current_section_bodies(bundle)
    _reseal_existing_manifest(bundle)
    with pytest.raises(BundleParseError, match="anchorable claim"):
        _harden_bundle(bundle, directive)


def test_inline_code_delimiters_do_not_pair_across_blank_block_boundary(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    course, directive = _write_live_shaped_corpus(tmp_path)
    bundle = tmp_path / "bundle"
    monkeypatch.chdir(course)
    _runner_module().run(directive, bundle)
    extracted = bundle / "extracted.md"
    extracted.write_text(
        extracted.read_text(encoding="utf-8").replace(
            "- Claim 1 has enough words to receive an evidence marker.",
            "- `unclosed opener\n\n"
            "- Visible [evidence: src-001] foreign marker.\n\n"
            "- `unrelated closer\n"
            "- Claim 1 has enough words to receive an evidence marker.",
            1,
        ),
        encoding="utf-8",
    )
    _accept_current_section_bodies(bundle)
    _reseal_existing_manifest(bundle)
    with pytest.raises(BundleParseError, match="foreign or ambiguous"):
        _harden_bundle(bundle, directive)


def test_inline_code_delimiters_do_not_pair_across_sibling_list_items(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    course, directive = _write_live_shaped_corpus(tmp_path)
    bundle = tmp_path / "bundle"
    monkeypatch.chdir(course)
    _runner_module().run(directive, bundle)
    extracted = bundle / "extracted.md"
    extracted.write_text(
        extracted.read_text(encoding="utf-8").replace(
            "- Claim 1 has enough words to receive an evidence marker.",
            "- `unclosed opener\n"
            "- Foreign [evidence: src-001] closer`\n"
            "- Claim 1 has enough words to receive an evidence marker.",
            1,
        ),
        encoding="utf-8",
    )
    _accept_current_section_bodies(bundle)
    _reseal_existing_manifest(bundle)
    with pytest.raises(BundleParseError, match="foreign or ambiguous"):
        _harden_bundle(bundle, directive)


def test_new_list_item_resets_type7_html_paragraph_state() -> None:
    lines = scan_markdown_lines(
        "outside paragraph\n- <custom-widget>\n  ## Fake\n\n## Real\n"
    )
    assert lines[2].heading_level is None
    assert lines[4].heading_level == 2
    assert lines[4].heading_text == "Real"


def test_indented_paragraph_continuation_preserves_multiline_code_span(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    course, directive = _write_live_shaped_corpus(tmp_path)
    bundle = tmp_path / "bundle"
    monkeypatch.chdir(course)
    _runner_module().run(directive, bundle)
    extracted = bundle / "extracted.md"
    extracted.write_text(
        extracted.read_text(encoding="utf-8").replace(
            "- Claim 1 has enough words to receive an evidence marker.",
            "- Text `code\n    [evidence: example]` continues.\n"
            "- Claim 1 has enough words to receive an evidence marker.",
            1,
        ),
        encoding="utf-8",
    )
    _accept_current_section_bodies(bundle)
    _reseal_existing_manifest(bundle)
    _harden_bundle(bundle, directive)
    hardened = extracted.read_text(encoding="utf-8")
    assert "[evidence: example]` continues. [evidence: src-006]" in hardened
    assert "Text `code [evidence:" not in hardened


def test_indented_list_html_literal_ends_at_sibling_item(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    course, directive = _write_live_shaped_corpus(tmp_path)
    bundle = tmp_path / "bundle"
    monkeypatch.chdir(course)
    _runner_module().run(directive, bundle)
    extracted = bundle / "extracted.md"
    metadata = json.loads((bundle / "metadata.json").read_text(encoding="utf-8"))
    second_title = metadata["provenance"][6]["section_title"]
    extracted.write_text(
        extracted.read_text(encoding="utf-8").replace(
            "- Claim 1 has enough words to receive an evidence marker.",
            f"- prose\n  <custom-widget>\n  ## {second_title}\n"
            "- Claim 1 has enough words to receive an evidence marker.",
            1,
        ),
        encoding="utf-8",
    )
    _accept_current_section_bodies(bundle)
    _reseal_existing_manifest(bundle)
    _harden_bundle(bundle, directive)


def test_literal_list_markers_do_not_replace_opener_container() -> None:
    lines = scan_markdown_lines(
        "- ```\n  - literal item\n  ## Fake\n  ```\n## Real\n"
    )
    assert lines[2].heading_level is None
    assert lines[4].heading_level == 2
    assert lines[4].heading_text == "Real"


def test_nested_list_exit_restores_parent_container() -> None:
    lines = scan_markdown_lines(
        "- outer\n  - inner\n  ## Still in outer\n  ```\n  unclosed parent literal\n"
        "## Real root boundary\n"
    )
    assert lines[2].heading_level is None
    assert lines[5].heading_level == 2
    assert lines[5].heading_text == "Real root boundary"


def test_inline_code_cannot_pair_from_nested_item_into_parent() -> None:
    body = "- outer\n  - `nested opener\n\n  Visible [evidence: evil] closer`\n"
    with pytest.raises(BundleParseError, match="foreign or ambiguous"):
        _anchor_extracted_claims(body, "owner")


def test_parent_list_container_survives_nested_blockquote() -> None:
    lines = scan_markdown_lines(
        "- outer\n  > quoted\n  ```\n  unclosed parent literal\n## Real\n"
    )
    assert lines[0].container_key[1] == lines[2].container_key[1]
    assert lines[3].is_literal
    assert lines[4].heading_level == 2
    assert lines[4].heading_text == "Real"


def test_lazy_blockquote_continuation_preserves_multiline_code_span() -> None:
    anchored, claim_count = _anchor_extracted_claims(
        "> `code\ncontinuation [evidence: example]` prose.\n", "owner"
    )
    assert claim_count == 1
    assert anchored.endswith(
        "continuation [evidence: example]` prose. [evidence: owner]\n"
    )


def test_non_one_ordered_marker_does_not_interrupt_paragraph_with_fence() -> None:
    with pytest.raises(BundleParseError, match="foreign or ambiguous"):
        _anchor_extracted_claims(
            "paragraph\n2. ``` [evidence: evil]\n", "owner"
        )


def test_same_line_html_close_does_not_leak_container_state() -> None:
    lines = scan_markdown_lines("<script></script>\n> quoted\n## Root\n")
    assert lines[0].is_literal
    assert lines[1].container_key == (1, None)
    assert lines[2].heading_level == 2
    assert lines[2].heading_text == "Root"


def test_backslash_does_not_escape_closer_inside_multiline_code_span() -> None:
    anchored, claim_count = _anchor_extracted_claims(
        "`literal\nmore \\` prose.\n", "owner"
    )
    assert claim_count == 1
    assert anchored == "`literal\nmore \\` prose. [evidence: owner]\n"


@pytest.mark.parametrize("marker", ["-", "+", "*", "1.", "1)"])
def test_root_list_interrupts_lazy_blockquote_paragraph(marker: str) -> None:
    indent = "   " if marker.startswith("1") else "  "
    body = (
        "> quoted paragraph\n"
        f"{marker} ```\n"
        f"{indent}[evidence: example]\n"
        f"{indent}```\n"
        "Visible claim.\n"
    )
    anchored, claim_count = _anchor_extracted_claims(body, "owner")
    assert claim_count == 2
    assert "[evidence: example] [evidence: owner]" not in anchored
    assert anchored.endswith("Visible claim. [evidence: owner]\n")


def test_adjacent_multiline_code_spans_anchor_after_last_closer_idempotently() -> None:
    body = "`one\n` prose `two\n`\n"
    anchored, claim_count = _anchor_extracted_claims(body, "owner")
    assert claim_count == 1
    assert anchored == "`one\n` prose `two\n` [evidence: owner]\n"
    repeated, repeated_count = _anchor_extracted_claims(anchored, "owner")
    assert repeated_count == 1
    assert repeated == anchored


def test_consumer_rejects_active_publication_transaction(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    course, directive = _write_live_shaped_corpus(tmp_path)
    bundle = tmp_path / "bundle"
    monkeypatch.chdir(course)
    _runner_module().run(directive, bundle)
    (bundle / ".texas-hardening-transaction.json").write_text(
        "{}\n", encoding="utf-8"
    )
    with pytest.raises(BundleParseError, match="transaction is still present"):
        load_bundle_outputs(bundle)


@pytest.mark.parametrize(
    ("marker", "indent"),
    [
        ("-", "  "),
        ("+", "  "),
        ("*", "  "),
        ("01.", "    "),
        ("000000001.", "           "),
    ],
)
def test_empty_start_one_list_interrupts_lazy_blockquote_and_binds_literal(
    marker: str, indent: str
) -> None:
    body = (
        "> quoted paragraph\n"
        f"{marker}\n"
        f"{indent}```\n"
        f"{indent}[evidence: example]\n"
        f"{indent}```\n"
        "Visible claim.\n"
    )
    anchored, claim_count = _anchor_extracted_claims(body, "owner")
    assert claim_count == 2
    assert "[evidence: example] [evidence: owner]" not in anchored
    assert anchored.endswith("Visible claim. [evidence: owner]\n")


def test_consumer_rejects_manifest_authenticated_status_disagreement(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    course, directive = _write_live_shaped_corpus(tmp_path)
    bundle = tmp_path / "bundle"
    monkeypatch.chdir(course)
    _runner_module().run(directive, bundle)
    result = yaml.safe_load((bundle / "result.yaml").read_text(encoding="utf-8"))
    result["status"] = "forged-status"
    (bundle / "result.yaml").write_text(
        yaml.safe_dump(result, sort_keys=False), encoding="utf-8"
    )
    _reseal_existing_manifest(bundle)
    with pytest.raises(BundleParseError, match="status disagree") as exc_info:
        load_bundle_outputs(bundle)
    assert exc_info.value.tag == "bundle.parsed.provenance-mismatch"


def test_five_space_list_padding_keeps_excess_content_indent() -> None:
    lines = scan_markdown_lines("-     ```\n  ## Fake\n## Real\n")
    assert lines[0].is_literal
    assert lines[1].heading_level is None
    assert lines[2].heading_level == 2
    assert lines[2].heading_text == "Real"


def test_consumer_rejects_non_string_published_statuses(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    course, directive = _write_live_shaped_corpus(tmp_path)
    bundle = tmp_path / "bundle"
    monkeypatch.chdir(course)
    _runner_module().run(directive, bundle)
    result = yaml.safe_load((bundle / "result.yaml").read_text(encoding="utf-8"))
    report = yaml.safe_load(
        (bundle / "extraction-report.yaml").read_text(encoding="utf-8")
    )
    result["status"] = ["complete"]
    report["overall_status"] = ["complete"]
    (bundle / "result.yaml").write_text(
        yaml.safe_dump(result, sort_keys=False), encoding="utf-8"
    )
    (bundle / "extraction-report.yaml").write_text(
        yaml.safe_dump(report, sort_keys=False), encoding="utf-8"
    )
    _reseal_existing_manifest(bundle)
    with pytest.raises(BundleParseError, match="non-empty status"):
        load_bundle_outputs(bundle)


def test_consumer_rejects_manifest_authenticated_run_identity_disagreement(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    course, directive = _write_live_shaped_corpus(tmp_path)
    bundle = tmp_path / "bundle"
    monkeypatch.chdir(course)
    _runner_module().run(directive, bundle)
    result = yaml.safe_load((bundle / "result.yaml").read_text(encoding="utf-8"))
    result["run_id"] = "substituted-run"
    (bundle / "result.yaml").write_text(
        yaml.safe_dump(result, sort_keys=False), encoding="utf-8"
    )
    _reseal_existing_manifest(bundle)
    with pytest.raises(BundleParseError, match="run identities disagree"):
        load_bundle_outputs(bundle)


def test_hardener_rejects_directive_mutated_after_bundle_generation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    course, directive = _write_live_shaped_corpus(tmp_path)
    bundle = tmp_path / "bundle"
    monkeypatch.chdir(course)
    _runner_module().run(directive, bundle)
    changed = yaml.safe_load(directive.read_text(encoding="utf-8"))
    changed["sources"][5]["expected_min_words"] = 0
    directive.write_text(yaml.safe_dump(changed, sort_keys=False), encoding="utf-8")
    with pytest.raises(BundleParseError, match="directive, bundle identity"):
        _harden_bundle(bundle, directive)


def test_tab_expanded_list_padding_outdents_two_space_root_heading() -> None:
    lines = scan_markdown_lines("-\t```\n  ## Boundary\n")
    assert lines[0].is_literal
    assert lines[1].heading_level == 2
    assert lines[1].heading_text == "Boundary"


def test_corpus_relative_slide_locator_stays_canonical_in_authority_metadata(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    course = tmp_path / "course"
    slide = course / "slides" / "slide-1-topic.md"
    slide.parent.mkdir(parents=True)
    slide.write_text("# Topic\n\nCanonical claim text.\n", encoding="utf-8")
    directive = tmp_path / "directive.yaml"
    directive.write_text(
        yaml.safe_dump(
            {
                "run_id": "relative-slide",
                "corpus_dir": str(course),
                "sources": [
                    {
                        "ref_id": "src-001",
                        "provider": "local_file",
                        "locator": "slides/slide-1-topic.md",
                        "role": "primary",
                        "expected_min_words": 1,
                    }
                ],
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    bundle = tmp_path / "bundle"
    _runner_module().run(directive, bundle)
    metadata = json.loads((bundle / "metadata.json").read_text(encoding="utf-8"))
    assert metadata["provenance"][0]["ref"] == "slides/slide-1-topic.md"
    assert metadata["source_authority"][0]["path"] == "slides/slide-1-topic.md"
    _harden_bundle(bundle, directive)


def test_tab_after_blockquote_marker_remains_claim_text() -> None:
    anchored, claim_count = _anchor_extracted_claims(">\tFactual claim.\n", "owner")
    assert claim_count == 1
    assert anchored == ">\tFactual claim. [evidence: owner]\n"


def test_multi_tab_list_padding_uses_expanded_columns() -> None:
    lines = scan_markdown_lines(
        "-\t\titem\n    ```\n    ## Fake\n    ```\n## Real\n"
    )
    assert lines[2].heading_level is None
    assert lines[4].heading_level == 2
    assert lines[4].heading_text == "Real"


def test_runner_rejects_forged_reserved_authority_locator(tmp_path: Path) -> None:
    source = tmp_path / "source.md"
    source.write_text("# Source\n\nClaim.\n", encoding="utf-8")
    directive = tmp_path / "directive.yaml"
    directive.write_text(
        yaml.safe_dump(
            {
                "run_id": "reserved-key",
                "sources": [
                    {
                        "ref_id": "src-001",
                        "provider": "local_file",
                        "locator": str(source),
                        "_authority_locator": "slides/forged.md",
                        "role": "primary",
                        "expected_min_words": 1,
                    }
                ],
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    runner = _runner_module()
    with pytest.raises(runner.DirectiveError, match="reserved internal key"):
        runner.run(directive, tmp_path / "bundle")


def test_mixed_tab_space_blockquote_preserves_code_and_prose_roles() -> None:
    lines = scan_markdown_lines(">\t  Evidence: literal\n> \tEvidence: claim\n")
    assert lines[0].is_literal
    assert not lines[1].is_literal
    anchored, claim_count = _anchor_extracted_claims(
        ">\t  Evidence: literal\n> \tEvidence: claim\n", "owner"
    )
    assert claim_count == 1
    assert anchored == (
        ">\t  Evidence: literal\n> \tEvidence: claim [evidence: owner]\n"
    )


def test_overwide_tab_list_padding_preserves_indented_code() -> None:
    lines = scan_markdown_lines("-\t  Evidence: literal\n  ## Still list content\n")
    assert lines[0].is_literal
    assert lines[1].heading_level is None


def test_corpus_relative_locator_cannot_escape_through_symlink(tmp_path: Path) -> None:
    course = tmp_path / "course"
    slides = course / "slides"
    slides.mkdir(parents=True)
    external = tmp_path / "external.md"
    external.write_text("# External\n\nClaim.\n", encoding="utf-8")
    link = slides / "slide-escape.md"
    try:
        link.symlink_to(external)
    except OSError:
        pytest.skip("symlink creation is unavailable on this platform")
    directive = tmp_path / "directive.yaml"
    directive.write_text(
        yaml.safe_dump(
            {
                "run_id": "symlink-escape",
                "corpus_dir": str(course),
                "sources": [
                    {
                        "ref_id": "src-001",
                        "provider": "local_file",
                        "locator": "slides/slide-escape.md",
                        "role": "primary",
                        "expected_min_words": 1,
                    }
                ],
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    runner = _runner_module()
    with pytest.raises(runner.DirectiveError, match="escapes corpus_dir"):
        runner.run(directive, tmp_path / "bundle")


def test_declared_corpus_wins_over_same_relative_path_in_process_cwd(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    corpus = tmp_path / "corpus"
    cwd = tmp_path / "cwd"
    corpus_slide = corpus / "slides" / "slide-1-topic.md"
    cwd_slide = cwd / "slides" / "slide-1-topic.md"
    corpus_slide.parent.mkdir(parents=True)
    cwd_slide.parent.mkdir(parents=True)
    corpus_slide.write_text("# Corpus\n\nCorpus authority claim.\n", encoding="utf-8")
    cwd_slide.write_text("# Wrong\n\nWrong cwd claim.\n", encoding="utf-8")
    directive = tmp_path / "directive.yaml"
    directive.write_text(
        yaml.safe_dump(
            {
                "run_id": "corpus-collision",
                "corpus_dir": str(corpus),
                "sources": [
                    {
                        "ref_id": "src-001",
                        "provider": "local_file",
                        "locator": "slides/slide-1-topic.md",
                        "role": "primary",
                        "expected_min_words": 1,
                    }
                ],
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    monkeypatch.chdir(cwd)
    bundle = tmp_path / "bundle"
    _runner_module().run(directive, bundle)
    extracted = (bundle / "extracted.md").read_text(encoding="utf-8")
    assert "Corpus authority claim" in extracted
    assert "Wrong cwd claim" not in extracted


def test_independent_blockquote_retires_stale_root_list_container() -> None:
    lines = scan_markdown_lines("- a\n> quote\n\n  ```\n## H\n")
    assert lines[3].is_literal
    assert lines[4].is_literal
    assert lines[4].heading_level is None


def test_nested_blockquote_pops_inner_list_but_retains_outer_list() -> None:
    lines = scan_markdown_lines(
        "- outer\n  - inner\n  > quote\n\n  ```\n## H\n"
    )
    assert lines[4].is_literal
    assert lines[5].heading_level == 2
    assert lines[5].heading_text == "H"


def test_entering_quote_marker_is_measured_after_outer_blockquote() -> None:
    body = "> - item\n>   > quote\n>\n>     Evidence: after\n"
    anchored, claim_count = _anchor_extracted_claims(body, "owner")
    assert claim_count >= 2
    assert anchored.endswith(">     Evidence: after [evidence: owner]\n")


def test_corpus_rejects_in_root_symlink_alias(tmp_path: Path) -> None:
    course = tmp_path / "course"
    slides = course / "slides"
    notes = course / "notes"
    slides.mkdir(parents=True)
    notes.mkdir()
    support = notes / "support.md"
    support.write_text("# Support\n\nNot slide authority.\n", encoding="utf-8")
    alias = slides / "slide-1-alias.md"
    try:
        alias.symlink_to(support)
    except OSError:
        pytest.skip("symlink creation is unavailable on this platform")
    directive = tmp_path / "directive.yaml"
    directive.write_text(
        yaml.safe_dump(
            {
                "run_id": "in-root-alias",
                "corpus_dir": str(course),
                "sources": [
                    {
                        "ref_id": "src-001",
                        "provider": "local_file",
                        "locator": "slides/slide-1-alias.md",
                        "role": "primary",
                        "expected_min_words": 1,
                    }
                ],
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    runner = _runner_module()
    with pytest.raises(runner.DirectiveError, match="escapes corpus_dir"):
        runner.run(directive, tmp_path / "bundle")


def test_quote_outdent_retires_invalid_lists_across_multiple_depths() -> None:
    body = (
        "- outer\n"
        "  > - inner\n"
        "> > quote\n"
        "\n"
        "    Evidence: literal after\n"
    )
    lines = scan_markdown_lines(body)
    assert lines[4].is_literal
    anchored, claim_count = _anchor_extracted_claims(body, "owner")
    assert "Evidence: literal after [evidence: owner]" not in anchored
    assert claim_count == 3
