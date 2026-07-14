from __future__ import annotations

import hashlib

import pytest

from app.marcus.lesson_plan import pass1_source_span_catalog as catalog_module
from app.marcus.lesson_plan.pass1_source_span_catalog import (
    Pass1SourceSpanCatalogError,
    Pass1SourceSpanV1,
    build_pass1_source_span_catalog,
    project_pass1_source_ref_ids,
)
from app.models.pass1_source_section import (
    Pass1AuthenticatedSourceSection,
    canonical_extracted_content_digest,
)

EXACT = "We can no longer rely on static training."
NEAR_PARAPHRASE = "cannot rely on static training"
SLIDE_4_TEXT = "Patients expect access."


def _source_id(path: str, text: str) -> str:
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return f"{path}|sha256:{digest}"


def _section(
    path: str,
    body: str,
    *,
    raw_source_text: str | None = None,
    extracted_digest: str | None = None,
) -> Pass1AuthenticatedSourceSection:
    source_id = _source_id(path, body if raw_source_text is None else raw_source_text)
    source_digest = source_id.split("|", 1)[1]
    return Pass1AuthenticatedSourceSection(
        source_id=source_id,
        source_content_digest=source_digest,
        extracted_content_digest=(
            canonical_extracted_content_digest(body)
            if extracted_digest is None
            else extracted_digest
        ),
        body=body,
    )


SLIDE_3_ID = _source_id("slides/slide-3-knowledge.md", EXACT)
SLIDE_4_ID = _source_id("slides/slide-4-consumer.md", SLIDE_4_TEXT)


def _catalog(*, slide_3: str = EXACT, slide_4: str = SLIDE_4_TEXT):
    return build_pass1_source_span_catalog(
        (
            _section("slides/slide-3-knowledge.md", slide_3),
            _section("slides/slide-4-consumer.md", slide_4),
        )
    )


def _entry_for_text(catalog, text: str):
    return next(entry for entry in catalog.entries if entry.text == text)


def test_catalog_carries_witnessed_exact_sentence_not_near_paraphrase() -> None:
    catalog = _catalog()

    exact = _entry_for_text(catalog, EXACT)

    assert exact.source_id == SLIDE_3_ID
    assert exact.source_path == "slides/slide-3-knowledge.md"
    assert exact.source_digest == SLIDE_3_ID.split("|", 1)[1]
    assert exact.start == 0
    assert exact.end == len(EXACT)
    assert all(entry.text != NEAR_PARAPHRASE for entry in catalog.entries)


def test_catalog_is_canonical_and_mutation_changes_identity() -> None:
    first = _catalog()
    second = _catalog()
    mutated = _catalog(slide_3=EXACT + " New evidence changes the source bytes.")

    assert first == second
    assert first.catalog_digest == second.catalog_digest
    assert first.catalog_digest != mutated.catalog_digest
    assert first.entries != mutated.entries


def test_extracted_generation_changes_span_identity_even_when_selected_text_stays() -> None:
    first = build_pass1_source_span_catalog(
        (
            _section(
                "slides/slide-3-knowledge.md",
                f"{EXACT} First extracted annotation.",
                raw_source_text=EXACT,
            ),
        )
    )
    second = build_pass1_source_span_catalog(
        (
            _section(
                "slides/slide-3-knowledge.md",
                f"{EXACT} Changed extracted annotation.",
                raw_source_text=EXACT,
            ),
        )
    )

    assert _entry_for_text(first, EXACT).source_id == _entry_for_text(
        second, EXACT
    ).source_id
    assert _entry_for_text(first, EXACT).span_id != _entry_for_text(
        second, EXACT
    ).span_id
    assert first.catalog_digest != second.catalog_digest


def test_catalog_rejects_raw_or_extracted_digest_role_substitution() -> None:
    valid = _section("slides/slide-3-knowledge.md", EXACT)
    wrong_raw = Pass1AuthenticatedSourceSection(
        source_id=valid.source_id,
        source_content_digest="sha256:" + "a" * 64,
        extracted_content_digest=valid.extracted_content_digest,
        body=valid.body,
    )
    wrong_extracted = Pass1AuthenticatedSourceSection(
        source_id=valid.source_id,
        source_content_digest=valid.source_content_digest,
        extracted_content_digest="sha256:" + "b" * 64,
        body=valid.body,
    )

    with pytest.raises(Pass1SourceSpanCatalogError, match="raw-source digest"):
        build_pass1_source_span_catalog((wrong_raw,))
    with pytest.raises(Pass1SourceSpanCatalogError, match="extracted digest"):
        build_pass1_source_span_catalog((wrong_extracted,))
    with pytest.raises(Pass1SourceSpanCatalogError, match="authenticated.*records"):
        build_pass1_source_span_catalog(((valid.source_id, valid.body),))  # type: ignore[arg-type]


def test_catalog_rejects_one_source_path_with_conflicting_raw_identities() -> None:
    with pytest.raises(Pass1SourceSpanCatalogError, match="duplicate source path"):
        build_pass1_source_span_catalog(
            (
                _section(
                    "slides/slide-3-knowledge.md",
                    "First extracted generation.",
                    raw_source_text="First raw generation.",
                ),
                _section(
                    "slides/slide-3-knowledge.md",
                    "Second extracted generation.",
                    raw_source_text="Second raw generation.",
                ),
            )
        )


def test_deserialized_span_rejects_offsets_that_disagree_with_exact_text() -> None:
    entry = _entry_for_text(_catalog(), EXACT)
    forged = entry.model_dump(mode="json")
    forged["end"] += 1
    forged["span_id"] = catalog_module._digest(  # noqa: SLF001 - causal corruption witness
        {
            "source_id": forged["source_id"],
            "extracted_content_digest": forged["extracted_content_digest"],
            "start": forged["start"],
            "end": forged["end"],
            "text": forged["text"],
        }
    ).replace("sha256:", "span:sha256:", 1)

    with pytest.raises(ValueError, match="offset range disagrees"):
        Pass1SourceSpanV1.model_validate(forged)


def test_catalog_excludes_text_repeated_across_source_slides() -> None:
    repeated = "This exact sentence appears on two slides."
    catalog = _catalog(
        slide_3=f"{repeated} Slide three has unique evidence.",
        slide_4=f"{repeated} Slide four has different evidence.",
    )

    assert all(entry.text != repeated for entry in catalog.entries)


def test_catalog_rejects_source_with_no_unique_selectable_span() -> None:
    repeated = "The same complete source text."
    with pytest.raises(Pass1SourceSpanCatalogError, match="no uniquely selectable"):
        build_pass1_source_span_catalog(
            (
                _section("slides/slide-3-knowledge.md", repeated),
                _section("slides/slide-4-consumer.md", repeated),
            )
        )


def test_catalog_sentence_span_includes_closing_quote() -> None:
    quoted = 'He said "Exact sentence." Next sentence.'
    catalog = build_pass1_source_span_catalog(
        (_section("slides/slide-3-knowledge.md", quoted),)
    )

    assert any(entry.text == 'He said "Exact sentence."' for entry in catalog.entries)
    assert all(not entry.text.startswith('" Next') for entry in catalog.entries)


def test_catalog_rejects_entry_or_serialized_size_over_bound(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(catalog_module, "_MAX_CATALOG_ENTRIES", 1)
    with pytest.raises(Pass1SourceSpanCatalogError, match="entry limit"):
        _catalog(slide_3="First sentence. Second sentence.")

    monkeypatch.setattr(catalog_module, "_MAX_CATALOG_ENTRIES", 4096)
    monkeypatch.setattr(catalog_module, "_MAX_CATALOG_BYTES", 1)
    with pytest.raises(Pass1SourceSpanCatalogError, match="byte limit"):
        _catalog()


@pytest.mark.parametrize(
    "source_sections",
    [
        (),
        (_section("slides/slide-3-knowledge.md", " "),),
        (
            Pass1AuthenticatedSourceSection(
                source_id="not-a-source-id",
                source_content_digest="sha256:" + "a" * 64,
                extracted_content_digest=canonical_extracted_content_digest(EXACT),
                body=EXACT,
            ),
        ),
        (
            _section("slides/slide-3-knowledge.md", EXACT),
            _section("slides/slide-3-knowledge.md", EXACT),
        ),
    ],
)
def test_catalog_rejects_missing_or_ambiguous_source_authority(
    source_sections: tuple[Pass1AuthenticatedSourceSection, ...],
) -> None:
    with pytest.raises(Pass1SourceSpanCatalogError):
        build_pass1_source_span_catalog(source_sections)


def test_projection_materializes_exact_bytes_and_removes_selection_ids() -> None:
    catalog = _catalog()
    selected = _entry_for_text(catalog, EXACT)
    plan = {
        "plan_units": [
            {
                "unit_id": "u03i1",
                "scope_decision": "in-scope",
                "source_ref_ids": [selected.span_id],
            }
        ]
    }

    projected = project_pass1_source_ref_ids(plan, catalog=catalog)

    assert projected["plan_units"][0]["source_refs"] == [EXACT]
    assert projected["plan_units"][0]["source_ref_ids"] == [selected.span_id]
    assert plan["plan_units"][0].get("source_refs") is None


@pytest.mark.parametrize("selection", [[], ["unknown"], ["duplicate", "duplicate"]])
def test_projection_rejects_empty_unknown_or_duplicate_ids(selection: list[str]) -> None:
    catalog = _catalog()
    if selection == ["duplicate", "duplicate"]:
        selected = _entry_for_text(catalog, EXACT).span_id
        selection = [selected, selected]
    plan = {
        "plan_units": [
            {
                "unit_id": "u03i1",
                "scope_decision": "in-scope",
                "source_ref_ids": selection,
            }
        ]
    }

    with pytest.raises(Pass1SourceSpanCatalogError):
        project_pass1_source_ref_ids(plan, catalog=catalog)


def test_projection_rejects_cross_source_selection_and_model_authored_text() -> None:
    catalog = _catalog()
    selected_3 = _entry_for_text(catalog, EXACT)
    selected_4 = _entry_for_text(catalog, SLIDE_4_TEXT)
    cross_source = {
        "plan_units": [
            {
                "unit_id": "u03i1",
                "scope_decision": "in-scope",
                "source_ref_ids": [selected_3.span_id, selected_4.span_id],
            }
        ]
    }
    authored_text = {
        "plan_units": [
            {
                "unit_id": "u03i1",
                "scope_decision": "in-scope",
                "source_ref_ids": [selected_3.span_id],
                "source_refs": [NEAR_PARAPHRASE],
            }
        ]
    }

    with pytest.raises(Pass1SourceSpanCatalogError, match="one source"):
        project_pass1_source_ref_ids(cross_source, catalog=catalog)
    with pytest.raises(Pass1SourceSpanCatalogError, match="model-authored"):
        project_pass1_source_ref_ids(authored_text, catalog=catalog)


def test_projection_rejects_stale_ids_after_source_mutation() -> None:
    original = _catalog()
    selected = _entry_for_text(original, EXACT)
    mutated = _catalog(slide_3=EXACT + " New evidence changes the source bytes.")
    plan = {
        "plan_units": [
            {
                "unit_id": "u03i1",
                "scope_decision": "in-scope",
                "source_ref_ids": [selected.span_id],
            }
        ]
    }

    with pytest.raises(Pass1SourceSpanCatalogError, match="unknown or stale"):
        project_pass1_source_ref_ids(plan, catalog=mutated)


def test_projection_rejects_more_than_six_selected_spans() -> None:
    text = "One. Two. Three. Four. Five. Six. Seven."
    catalog = build_pass1_source_span_catalog(
        (_section("slides/slide-3-knowledge.md", text),)
    )
    selected = [entry.span_id for entry in catalog.entries[:7]]
    assert len(selected) == 7

    with pytest.raises(Pass1SourceSpanCatalogError, match="six-span"):
        project_pass1_source_ref_ids(
            {
                "plan_units": [
                    {
                        "unit_id": "u03i1",
                        "scope_decision": "in-scope",
                        "source_ref_ids": selected,
                    }
                ]
            },
            catalog=catalog,
        )
