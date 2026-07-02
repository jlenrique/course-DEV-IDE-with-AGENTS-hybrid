"""Leg-E AC#3/#4/#5/#6 — audit driver hermetic battery (RED-first).

Covers: manifest shape + coverage pin (M-9), S-2 classification (incl. the
Texas T-7 indeterminate floor and classifier TOTALITY per M-5), S-1 ledger
write mapping with Dan's wording-triple filing gate, the spec digest recipe +
idempotency (tmp_path-only ledgers, AC#6), exit tiers per S-3, the pre-flight
llms.txt VOID, --dry-run, --ledger-path default = real SSOT, doc-sources
stamping, and D-4 lock immunity.

Network discipline: per-test `responses.RequestsMock()` serving the RECORDED
real-page fixtures at their REAL URLs (provenance:
tests/fixtures/retrieval/gamma_docs/README.md). No live calls.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

import pytest
import responses
import yaml

from scripts.utilities import audit_gamma_docs as audit

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "retrieval" / "gamma_docs"
DOC_SOURCES_PATH = (
    REPO_ROOT / "skills" / "gamma-api-mastery" / "references" / "doc-sources.yaml"
)
LOCK_PATH = REPO_ROOT / "state" / "config" / "gamma-learned-rules.lock"

IMAGE_MODELS_URL = "https://developers.gamma.app/reference/image-model-accepted-values.md"
PARAMS_URL = "https://developers.gamma.app/guides/generate-api-parameters-explained.md"
ASYNC_URL = "https://developers.gamma.app/guides/async-patterns-and-polling.md"
THEMES_URL = "https://developers.gamma.app/workspace/list-themes.md"
PREFLIGHT_URL = "https://developers.gamma.app/llms.txt"
CHANGELOG_URL = "https://developers.gamma.app/changelog/readme.md"

STANDING_ID = "obs-gamma-burst-throttle-401-not-429-2026-06-25"
"""The grandfathered standing candidate the burst-429 item cites (real SSOT seed)."""

_FIXTURE_BY_URL = {
    IMAGE_MODELS_URL: "image_model_accepted_values.md",
    PARAMS_URL: "generate_api_parameters_explained.md",
    ASYNC_URL: "async_patterns_and_polling.md",
    THEMES_URL: "list_themes.md",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _serve(rsps: responses.RequestsMock, url: str, *, status: int = 200) -> None:
    rsps.get(url, body=(FIXTURE_DIR / _FIXTURE_BY_URL[url]).read_bytes(), status=status)


def _serve_preflight(rsps: responses.RequestsMock, *, ok: bool = True) -> None:
    if ok:
        rsps.get(PREFLIGHT_URL, body=b"# developers.gamma.app llms.txt index\n")
    else:
        import requests as _requests

        rsps.get(PREFLIGHT_URL, body=_requests.exceptions.ConnectionError("site down"))


def _page_for(url: str) -> dict[str, Any]:
    """Fetch one fixture-served page through the driver's dispatch path."""
    with responses.RequestsMock() as rsps:
        _serve(rsps, url)
        return audit.fetch_page(url, fetch_interval_s=0.0)


def _failed_page(url: str, *, status: int = 500) -> dict[str, Any]:
    with responses.RequestsMock() as rsps:
        _serve(rsps, url, status=status)
        return audit.fetch_page(url, fetch_interval_s=0.0)


def _image_model_item(**overrides: Any) -> dict[str, Any]:
    item = {
        "item_id": "enum-parity-image-model",
        "kind": "enum-parity",
        "code_ref": "app.specialists.gary._act:IMAGE_MODEL_VALUES",
        "doc_url": IMAGE_MODELS_URL,
        "comparator": "enum-membership",
        "extraction": {
            "anchor": "### Standard models",
            "until": "### Output dimensions",
            "collect": "inline-code",
        },
        "consequence": (
            "a styleguide image_model may 404 at Gary dispatch or miss a cheaper "
            "documented model."
        ),
    }
    item.update(overrides)
    return item


def _text_mode_item(**overrides: Any) -> dict[str, Any]:
    item = {
        "item_id": "enum-parity-text-mode",
        "kind": "enum-parity",
        "code_ref": "app.specialists.gary._act:TEXT_MODE_VALUES",
        "doc_url": PARAMS_URL,
        "comparator": "enum-membership",
        "extraction": {
            "anchor": "#### `textMode`",
            "until": "#### `format`",
            "line_pattern": "You can choose",
            "collect": "inline-code",
        },
        "consequence": (
            "text_mode enum drift silently rejects valid styleguides or ships "
            "invalid ones."
        ),
    }
    item.update(overrides)
    return item


def _burst_429_item(**overrides: Any) -> dict[str, Any]:
    item = {
        "item_id": "doc-fact-burst-throttle-429",
        "kind": "doc-fact",
        "expected_documented": "429 Too Many Requests",
        "doc_url": ASYNC_URL,
        "comparator": "literal-presence",
        "extraction": {"anchor": "#### Handling a 429 response"},
        "standing_candidate": "obs-gamma-burst-throttle-401-not-429-2026-06-25",
        "consequence": "retry/backoff keyed to 429 misses the empirical 401 burst-throttle signal.",
    }
    item.update(overrides)
    return item


def _probe_item(**overrides: Any) -> dict[str, Any]:
    item = {
        "item_id": "probe-absent-anchor-teeth",
        "kind": "probe",
        "expected_documented": "never-found-anywhere",
        "doc_url": ASYNC_URL,
        "comparator": "literal-presence",
        "extraction": {"anchor": "#### zz-leg-e-probe-anchor-known-absent"},
        "consequence": (
            "probe: witnesses the doc-restructure detection path with zero "
            "confirmed writes."
        ),
    }
    item.update(overrides)
    return item


def _seed_standing(tmp_path: Path, observation_id: str = STANDING_ID) -> Path:
    """Seed the tmp ledger with a standing candidate (P5: citations are verified
    against the ledger, so tests that expect a standing-candidate write must
    seed the cited observation first — mirroring the real SSOT's grandfathered
    seeds)."""
    ledger = tmp_path / "ledger.jsonl"
    seed = {
        "observation_id": observation_id,
        "output_digest": "sha256:seed-standing-candidate",
        "status": "candidate",
        "behavior": "seed (grandfathered standing candidate stand-in)",
    }
    with ledger.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(seed, sort_keys=True, separators=(",", ":")) + "\n")
    return ledger


def _real_manifest_item(item_id: str) -> dict[str, Any]:
    items = audit.load_audit_manifest(audit.DEFAULT_MANIFEST_PATH)
    return next(i for i in items if i["item_id"] == item_id)


def _page_with_body(
    url: str, body: str, *, content_type: str = "text/plain"
) -> dict[str, Any]:
    with responses.RequestsMock() as rsps:
        rsps.get(url, body=body.encode("utf-8"), content_type=content_type)
        return audit.fetch_page(url, fetch_interval_s=0.0)


def _write_manifest(tmp_path: Path, items: list[dict[str, Any]]) -> Path:
    payload = {
        "schema_version": "1.0",
        "derived_from": "skills/gamma-api-mastery/references/doc-sources.yaml",
        "preflight_url": PREFLIGHT_URL,
        "items": items,
    }
    path = tmp_path / "manifest.yaml"
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    return path


def _run(
    tmp_path: Path,
    items: list[dict[str, Any]],
    *,
    serve_urls: list[str] | None = None,
    serve_status: int = 200,
    status_by_url: dict[str, int] | None = None,
    preflight_ok: bool = True,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Run the driver end-to-end against fixture-served pages; return artifacts."""
    manifest = _write_manifest(tmp_path, items)
    ledger = tmp_path / "ledger.jsonl"
    evidence = tmp_path / "evidence"
    doc_sources = tmp_path / "doc-sources.yaml"
    shutil.copyfile(DOC_SOURCES_PATH, doc_sources)
    urls = serve_urls if serve_urls is not None else sorted(
        {i["doc_url"] for i in items}
    )
    with responses.RequestsMock(assert_all_requests_are_fired=False) as rsps:
        _serve_preflight(rsps, ok=preflight_ok)
        for url in urls:
            _serve(rsps, url, status=(status_by_url or {}).get(url, serve_status))
        exit_code = audit.run_audit(
            manifest_path=manifest,
            ledger_path=ledger,
            evidence_dir=evidence,
            doc_sources_path=doc_sources,
            dry_run=dry_run,
            fetch_interval_s=0.0,
        )
    report_path = evidence / "run-report.json"
    report = (
        json.loads(report_path.read_text(encoding="utf-8"))
        if report_path.exists()
        else None
    )
    return {
        "exit": exit_code,
        "report": report,
        "ledger": ledger,
        "evidence": evidence,
        "doc_sources": doc_sources,
        "manifest": manifest,
    }


def _ledger_rows(ledger: Path) -> list[dict[str, Any]]:
    if not ledger.exists():
        return []
    return [
        json.loads(line)
        for line in ledger.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


# ---------------------------------------------------------------------------
# AC#3 — the committed manifest (data, not code)
# ---------------------------------------------------------------------------


def test_real_manifest_loads_validates_and_cites_doc_sources() -> None:
    items = audit.load_audit_manifest(audit.DEFAULT_MANIFEST_PATH)
    assert items, "committed audit manifest must be non-empty"
    payload = yaml.safe_load(
        Path(audit.DEFAULT_MANIFEST_PATH).read_text(encoding="utf-8")
    )
    assert payload["derived_from"].endswith("doc-sources.yaml"), (
        "S-4/A-7: the manifest URL set derives from + cites doc-sources.yaml"
    )
    doc_sources = yaml.safe_load(DOC_SOURCES_PATH.read_text(encoding="utf-8"))
    key_pages = {
        page["url"]
        for source in doc_sources["doc_sources"]
        for page in source.get("key_pages", [])
    }
    changelog_urls = {
        source["url"]
        for source in doc_sources["doc_sources"]
        if source.get("type") == "changelog"
    }
    allowed = key_pages | changelog_urls
    for item in items:
        assert item["doc_url"] in allowed, (
            f"{item['item_id']}: doc_url {item['doc_url']!r} not cataloged in "
            f"doc-sources.yaml (manifest must derive from it)"
        )


def test_real_manifest_covers_every_validator_enum_check() -> None:
    """M-9 coverage pin: every _ENUM_CHECKS frozenset has an enum-parity item
    whose dotted code_ref resolves to the SAME object (identity, no third copy)."""
    from scripts.utilities.validate_gamma_style_guides import _ENUM_CHECKS

    items = audit.load_audit_manifest(audit.DEFAULT_MANIFEST_PATH)
    resolved = [
        audit.resolve_code_ref(item["code_ref"])
        for item in items
        if item["kind"] == "enum-parity"
    ]
    for key, enum_obj in _ENUM_CHECKS.items():
        assert any(r is enum_obj for r in resolved), (
            f"_ENUM_CHECKS[{key!r}] has no enum-parity audit item whose code_ref "
            f"resolves to it (AC#3 coverage pin)"
        )


def test_real_manifest_enum_items_are_pointers_not_literals() -> None:
    """W-3: code_ref = importable dotted name; the manifest NEVER holds enum literals."""
    items = audit.load_audit_manifest(audit.DEFAULT_MANIFEST_PATH)
    for item in items:
        if item["kind"] != "enum-parity":
            continue
        assert re.fullmatch(r"[\w.]+:[A-Za-z_]\w*", item["code_ref"]), item["item_id"]
        assert "expected_documented" not in item, (
            f"{item['item_id']}: enum-parity items must not carry value literals "
            f"(no second SSOT)"
        )


def test_real_manifest_has_exactly_one_labeled_probe_with_absent_anchor() -> None:
    items = audit.load_audit_manifest(audit.DEFAULT_MANIFEST_PATH)
    probes = [i for i in items if i["kind"] == "probe"]
    assert len(probes) == 1, "AC#3: exactly ONE labeled kind: probe item"
    probe = probes[0]
    fixture_name = _FIXTURE_BY_URL.get(probe["doc_url"])
    assert fixture_name is not None, (
        "probe must target a fixtured page so its absent-anchor claim is "
        "verifiable hermetically"
    )
    text = (FIXTURE_DIR / fixture_name).read_text(encoding="utf-8")
    assert probe["extraction"]["anchor"] not in text, (
        "the probe anchor must be KNOWN-ABSENT (live TEETH witness, Murat M-7)"
    )


def test_real_manifest_carries_required_doc_fact_and_findings_items() -> None:
    items = {i["item_id"]: i for i in audit.load_audit_manifest(audit.DEFAULT_MANIFEST_PATH)}

    burst = items["doc-fact-burst-throttle-429"]
    assert burst["standing_candidate"] == "obs-gamma-burst-throttle-401-not-429-2026-06-25"
    assert "429" in str(burst["expected_documented"])

    header = items["doc-fact-ratelimit-burst-header"]
    assert header["expected_documented"] == "x-ratelimit-remaining-burst"

    polling = items["doc-fact-polling-interval-5s"]
    assert "5" in str(polling["expected_documented"])

    themes = items["doc-fact-list-themes-limit-50"]
    assert themes["comparator"] == "numeric"
    assert int(themes["expected_documented"]) == 50

    canary = items["doc-fact-changelog-canary"]
    assert canary["doc_url"].endswith("changelog/readme.md")

    tags = items["finding-imageoptions-discrete-tags-field"]
    assert tags.get("findings_only") is True
    preset = items["finding-imageoptions-stylepreset-style-composition"]
    assert preset.get("findings_only") is True

    lang = items["enum-parity-text-language"]
    assert lang["code_ref"].endswith("TEXT_LANGUAGE_VALUES")


@pytest.mark.parametrize("bad", [None, "", "   "], ids=["null", "empty", "whitespace"])
def test_manifest_loader_rejects_blank_expected_documented(
    tmp_path: Path, bad: Any
) -> None:
    """P2 (review): a None/empty/whitespace-only `expected_documented` is a
    manifest DEFECT — fail-loud ManifestError at load, never a vacuous confirm."""
    manifest = _write_manifest(tmp_path, [_burst_429_item(expected_documented=bad)])
    with pytest.raises(audit.ManifestError, match="expected_documented"):
        audit.load_audit_manifest(manifest)


# ---------------------------------------------------------------------------
# S-2 classification (Winston W-5 × Amelia A-2 × Texas T-7)
# ---------------------------------------------------------------------------


def test_classify_transport_failure_is_indeterminate() -> None:
    page = {"ok": False, "row": None, "error": "transport: DNS boom"}
    result = audit.classify_item(_text_mode_item(), page)
    assert result["terminal_state"] == "indeterminate"


def test_classify_http_failure_is_indeterminate() -> None:
    page = _failed_page(PARAMS_URL, status=500)
    result = audit.classify_item(_text_mode_item(), page)
    assert result["terminal_state"] == "indeterminate"


def test_classify_anchor_absent_is_doc_restructure_drift() -> None:
    page = _page_for(ASYNC_URL)
    result = audit.classify_item(_probe_item(), page)
    assert result["terminal_state"] == "drift-detected"
    assert result["drift_kinds"] == ["doc-restructure"]


def test_classify_enum_drift_is_asymmetric_with_distinct_kinds() -> None:
    """A-2: enum-value-absent-from-docs -> doc-drift; documented-absent-from-enum
    -> coverage-gap. The recorded image-model page carries REAL drift both ways."""
    page = _page_for(IMAGE_MODELS_URL)
    result = audit.classify_item(_image_model_item(), page)
    assert result["terminal_state"] == "drift-detected"
    assert set(result["drift_kinds"]) == {"doc-drift", "coverage-gap"}
    assert "imagen-4-fast" in result["diffs"]["doc-drift"], (
        "enum values absent from the live docs page (probe-grounded)"
    )
    assert "qwen-image" in result["diffs"]["doc-drift"]
    assert "flux-1-quick" in result["diffs"]["coverage-gap"], (
        "documented models absent from IMAGE_MODEL_VALUES (probe-grounded)"
    )
    assert result["diffs"]["doc-drift"] == sorted(result["diffs"]["doc-drift"])
    assert result["diffs"]["coverage-gap"] == sorted(result["diffs"]["coverage-gap"])


def test_classify_matching_enum_is_confirmed() -> None:
    page = _page_for(PARAMS_URL)
    result = audit.classify_item(_text_mode_item(), page)
    assert result["terminal_state"] == "confirmed", result.get("reason")
    assert result["drift_kinds"] == []


def test_classify_known_losses_can_never_mint_confirmed() -> None:
    """T-7 indeterminate floor."""
    page = _page_for(PARAMS_URL)
    row = page["row"].model_copy(deep=True)
    row.provider_metadata["gamma_docs"]["known_losses"] = ["partial_render"]
    result = audit.classify_item(
        _text_mode_item(), {"ok": True, "row": row, "error": None}
    )
    assert result["terminal_state"] == "indeterminate"


def test_classify_ambiguous_multi_anchor_is_indeterminate() -> None:
    page = _page_for(PARAMS_URL)
    row = page["row"].model_copy(
        update={"body": page["row"].body + "\n\n#### `textMode` (duplicated section)\n"}
    )
    result = audit.classify_item(
        _text_mode_item(), {"ok": True, "row": row, "error": None}
    )
    assert result["terminal_state"] == "indeterminate"


def test_classify_doc_fact_literals_confirm_on_recorded_pages() -> None:
    page = _page_for(ASYNC_URL)
    for item in (
        _burst_429_item(),
        {
            "item_id": "doc-fact-ratelimit-burst-header",
            "kind": "doc-fact",
            "expected_documented": "x-ratelimit-remaining-burst",
            "doc_url": ASYNC_URL,
            "comparator": "literal-presence",
            "extraction": {"anchor": "### Rate limit headers and adaptive polling"},
            "consequence": "pacing logic reads this header; a rename breaks adaptive throttling.",
        },
        {
            "item_id": "doc-fact-polling-interval-5s",
            "kind": "doc-fact",
            "expected_documented": "Use 5-second polling intervals",
            "doc_url": ASYNC_URL,
            "comparator": "literal-presence",
            "extraction": {"anchor": "### Best practices"},
            "consequence": "poller cadence grounded on this recommendation.",
        },
    ):
        result = audit.classify_item(item, page)
        assert result["terminal_state"] == "confirmed", (item["item_id"], result)


def test_classify_doc_fact_literal_absent_is_drift() -> None:
    page = _page_for(ASYNC_URL)
    item = _burst_429_item(expected_documented="418 I'm a teapot")
    result = audit.classify_item(item, page)
    assert result["terminal_state"] == "drift-detected"
    assert result["drift_kinds"] == ["doc-drift"]


def test_classify_numeric_comparator_confirms_themes_limit_50() -> None:
    page = _page_for(THEMES_URL)
    item = {
        "item_id": "doc-fact-list-themes-limit-50",
        "kind": "doc-fact",
        "expected_documented": 50,
        "doc_url": THEMES_URL,
        "comparator": "numeric",
        "extraction": {
            "anchor": "### Pagination",
            "until": "## List themes",
            "value_pattern": "`limit` \\(1-(\\d+)",
        },
        "consequence": "the validator's --check-existence caps list_themes at this limit.",
    }
    result = audit.classify_item(item, page)
    assert result["terminal_state"] == "confirmed", result.get("reason")
    wrong = dict(item, expected_documented=25)
    assert audit.classify_item(wrong, page)["terminal_state"] == "drift-detected"


def test_classify_not_enumerated_expectation() -> None:
    """image_style_preset: docs treat imageOptions.style as free text; the audit
    watches for Gamma INTRODUCING an enumerated style vocabulary. P7 shape:
    collect over the WHOLE scoped section (no narrowing line_pattern) with
    field-name/cross-ref exclude_tokens + a positive free-text witness."""
    page = _page_for(PARAMS_URL)
    item = {
        "item_id": "enum-parity-image-style-preset",
        "kind": "enum-parity",
        "code_ref": "app.specialists.gary._act:IMAGE_STYLE_PRESET_VALUES",
        "doc_url": PARAMS_URL,
        "comparator": "enum-membership",
        "extraction": {
            "anchor": "**`imageOptions.style`**",
            "until": "**What about accent images?**",
            "collect": "inline-code",
            "exclude_tokens": [
                "imageOptions.style",
                "imageOptions.source",
                "aiGenerated",
            ],
            "expectation": "not-enumerated",
            "witness_pattern": "one or multiple words to define the visual style",
        },
        "consequence": "a doc-side style enum would need reconciling with Gary's preset layer.",
    }
    result = audit.classify_item(item, page)
    assert result["terminal_state"] == "confirmed", result.get("reason")
    # If docs began enumerating, the same item must flip to drift.
    row = page["row"].model_copy(
        update={
            "body": page["row"].body.replace(
                "**`imageOptions.style`** *(optional)*",
                "**`imageOptions.style`** *(optional)*\n\nYou can choose between "
                "`vivid` or `natural`",
            )
        }
    )
    flipped = audit.classify_item(item, {"ok": True, "row": row, "error": None})
    assert flipped["terminal_state"] == "drift-detected"


def test_real_manifest_style_item_catches_enumeration_any_phrasing() -> None:
    """P7 RED probe: an enumeration phrased WITHOUT the old `line_pattern`
    ("You can choose") must still drift — collection runs over the whole
    scoped section, not a single sentence shape."""
    item = _real_manifest_item("enum-parity-image-style-preset")
    page = _page_for(PARAMS_URL)
    assert audit.classify_item(item, page)["terminal_state"] == "confirmed", (
        "pristine free-text section (with its witness sentence) confirms"
    )
    row = page["row"].model_copy(
        update={
            "body": page["row"].body.replace(
                "**`imageOptions.style`** *(optional)*",
                "**`imageOptions.style`** *(optional)*\n\nChoose from `vivid` "
                "or `natural`.",
            )
        }
    )
    flipped = audit.classify_item(item, {"ok": True, "row": row, "error": None})
    assert flipped["terminal_state"] == "drift-detected", (
        "line_pattern-missed enumeration must NOT mint confirmed (P7)",
        flipped.get("reason"),
    )


def test_not_enumerated_empty_collection_needs_positive_witness() -> None:
    """P7 RED probe: zero tokens is NOT a positive finding — without the
    declared free-text witness the item is indeterminate (T-7), never confirmed."""
    item = _real_manifest_item("enum-parity-image-style-preset")
    page = _page_for(PARAMS_URL)
    witness_sentence = (
        "You can add one or multiple words to define the visual style of the "
        "images you want."
    )
    assert witness_sentence in page["row"].body, "fixture must carry the witness"
    gutted = page["row"].body.replace(witness_sentence, "Details forthcoming.")
    row = page["row"].model_copy(update={"body": gutted})
    result = audit.classify_item(item, {"ok": True, "row": row, "error": None})
    assert result["terminal_state"] == "indeterminate", (
        "empty token collection without the positive witness must not mint "
        "confirmed (P7)",
        result.get("reason"),
    )


def test_changelog_canary_html_page_cannot_confirm() -> None:
    """P8 RED probe: a 200 HTML page (wrong Content-Type) must not confirm the
    serving-markdown canary — the content_type_not_markdown known_losses
    sentinel floors it to indeterminate (T-7)."""
    canary = _real_manifest_item("doc-fact-changelog-canary")
    html = (
        "<!DOCTYPE html><html><head><style>a {color: #fff}</style></head>"
        '<body><h1>Changelog</h1><a href="#top">top</a> issue #42</body></html>'
    )
    page = _page_with_body(CHANGELOG_URL, html, content_type="text/html")
    result = audit.classify_item(canary, page)
    assert result["terminal_state"] == "indeterminate", (
        "HTML page confirmed the markdown canary (P8)",
        result.get("reason"),
    )


def test_changelog_canary_requires_line_anchored_heading() -> None:
    """P8: the canary literal is a LINE-ANCHORED markdown heading. A heading at
    byte 0 or mid-page confirms; loose '#' characters do not."""
    canary = _real_manifest_item("doc-fact-changelog-canary")
    top = _page_with_body(
        CHANGELOG_URL, "# Changelog\n\n* entry one\n",
        content_type="text/markdown; charset=utf-8",
    )
    assert audit.classify_item(canary, top)["terminal_state"] == "confirmed"
    mid = _page_with_body(CHANGELOG_URL, "intro paragraph\n\n# Releases\nbody\n")
    assert audit.classify_item(canary, mid)["terminal_state"] == "confirmed"
    loose = _page_with_body(
        CHANGELOG_URL, "color #fff and issue #42 but no heading line\n"
    )
    assert audit.classify_item(canary, loose)["terminal_state"] == "drift-detected", (
        "loose '#' characters must not satisfy the markdown-heading canary (P8)"
    )


@pytest.mark.parametrize(
    "mutation",
    [
        {"extraction": None},
        {"extraction": {}},
        {"comparator": "quantum-vibes"},
        {"code_ref": "app.specialists.gary._act:DOES_NOT_EXIST"},
        {"code_ref": "no.such.module:X"},
        {"code_ref": "app.specialists.gary._act:REPO_ROOT"},  # not a set
        {"extraction": {"anchor": "### Pagination", "value_pattern": "(((broken"}},
    ],
    ids=[
        "extraction-none",
        "extraction-empty",
        "unknown-comparator",
        "missing-attr",
        "missing-module",
        "non-set-code-ref",
        "invalid-regex",
    ],
)
def test_classifier_totality_never_raises(mutation: dict[str, Any]) -> None:
    """M-5: exactly-one-of-three, no exception escape, for malformed inputs."""
    page = _page_for(PARAMS_URL)
    item = _text_mode_item()
    item = copy.deepcopy(item)
    item.update(mutation)
    if mutation.get("extraction") and "value_pattern" in mutation["extraction"]:
        item["comparator"] = "numeric"
        item["expected_documented"] = 50
    result = audit.classify_item(item, page)
    assert result["terminal_state"] in ("confirmed", "drift-detected", "indeterminate")
    # Malformed audit tooling input can never certify or accuse the docs.
    if "code_ref" in mutation or "comparator" in mutation or not mutation.get("extraction"):
        assert result["terminal_state"] == "indeterminate", (mutation, result)


def test_classifier_totality_on_degenerate_pages() -> None:
    for page in (
        {"ok": True, "row": None, "error": None},
        {"ok": False, "row": None, "error": None},
        None,
    ):
        result = audit.classify_item(_text_mode_item(), page)
        assert result["terminal_state"] == "indeterminate"


# ---------------------------------------------------------------------------
# S-1 ledger-write mapping + wording-triple gate + digest recipe (AC#5)
# ---------------------------------------------------------------------------


def test_drift_always_writes_and_carries_wording_triple(tmp_path: Path) -> None:
    art = _run(tmp_path, [_image_model_item()])
    rows = _ledger_rows(art["ledger"])
    assert rows, "drift-detected must ALWAYS write (S-1)"
    for obs in rows:
        behavior = obs["behavior"]
        assert "DOCUMENTED:" in behavior
        assert "OBSERVED:" in behavior
        assert "CONSEQUENCE:" in behavior
        assert "https://developers.gamma.app" in behavior
        assert obs["status"] == "candidate"
        assert obs["source_component"] == "scripts/utilities/audit_gamma_docs.py"
    # Distinct observation kinds for the two drift directions (A-2).
    kinds = {obs["kind"] for obs in rows}
    assert kinds == {"doc-drift", "coverage-gap"}


def test_confirmed_without_standing_candidate_never_writes(tmp_path: Path) -> None:
    art = _run(tmp_path, [_text_mode_item()])
    assert art["exit"] == audit.EXIT_OK
    assert _ledger_rows(art["ledger"]) == [], (
        "plain 'docs agree with code' leaves residue in the run report only (S-1)"
    )


def test_confirmed_resolving_standing_candidate_writes_citing_it(tmp_path: Path) -> None:
    _seed_standing(tmp_path)
    art = _run(tmp_path, [_burst_429_item()])
    rows = [o for o in _ledger_rows(art["ledger"]) if o["observation_id"] != STANDING_ID]
    assert len(rows) == 1, (
        "the 401!=429 item must write in EITHER direction (John J-1 liveness rider)"
    )
    obs = rows[0]
    assert obs["resolves_observation_id"] == STANDING_ID
    assert STANDING_ID in obs["behavior"]
    # P11: docs-still-429 direction — the candidate STANDS (re-confirmed against
    # the live docs); it is never worded as resolved/retired.
    behavior = obs["behavior"]
    assert "STANDS" in behavior, behavior
    assert "resolved" not in behavior.lower(), behavior
    assert "retired" not in behavior.lower(), behavior


def test_standing_candidate_missing_from_ledger_is_rejected_not_filed(
    tmp_path: Path,
) -> None:
    """P5 RED probe: a cited standing candidate that does NOT exist in the
    ledger is a dangling citation — reject-and-report, never write."""
    item = _burst_429_item(standing_candidate="obs-DOES-NOT-EXIST")
    art = _run(tmp_path, [item])
    assert _ledger_rows(art["ledger"]) == [], (
        "a standing-candidate write citing a nonexistent observation_id is a "
        "dangling citation (P5)"
    )
    rejected = art["report"]["ledger"]["rejected"]
    assert any("obs-DOES-NOT-EXIST" in json.dumps(r) for r in rejected), (
        "the rejection must be visible in the run report",
        rejected,
    )


def test_indeterminate_and_doc_restructure_never_write(tmp_path: Path) -> None:
    # doc-restructure: real page, absent anchor (non-probe item).
    restructure = _text_mode_item(
        item_id="enum-parity-text-mode-moved",
        extraction={"anchor": "#### `textModeRenamed`", "line_pattern": "You can choose"},
    )
    art = _run(tmp_path, [restructure])
    assert art["exit"] == audit.EXIT_DRIFT, "doc-restructure is LOUD + non-zero (S-2)"
    assert _ledger_rows(art["ledger"]) == [], (
        "doc-restructure is audit-tooling housekeeping, not Gamma-behavior "
        "divergence — run-report only (S-2)"
    )
    # indeterminate: transport-failed page.
    sub = tmp_path / "b2"
    sub.mkdir(exist_ok=True)
    art2 = _run(sub, [_text_mode_item()], serve_status=503)
    assert _ledger_rows(art2["ledger"]) == []


def test_probe_and_findings_only_never_write(tmp_path: Path) -> None:
    tags_item = {
        "item_id": "finding-imageoptions-discrete-tags-field",
        "kind": "doc-fact",
        "expected_documented": "imageOptions.tags",
        "doc_url": PARAMS_URL,
        "comparator": "literal-presence",
        "extraction": {"anchor": "#### imageOptions", "until": "#### cardOptions"},
        "findings_only": True,
        "consequence": "answers the keywords-routing field-surface question (J-7); evidence only.",
    }
    # A real confirmed item keeps the run non-VOID (P6), so the write phase is
    # actually reached — the probe/findings never-write claim stays non-vacuous
    # under the P1 VOID write-gate.
    art = _run(tmp_path, [_probe_item(), tags_item, _text_mode_item()])
    assert art["exit"] == audit.EXIT_OK
    assert _ledger_rows(art["ledger"]) == []
    report = art["report"]
    states = {i["item_id"]: i["terminal_state"] for i in report["items"]}
    assert states["probe-absent-anchor-teeth"] == "drift-detected"
    assert states["finding-imageoptions-discrete-tags-field"] == "drift-detected", (
        "the finding answer (no discrete tags field documented) surfaces in the "
        "report even though it never files"
    )


def test_wording_triple_gate_rejects_missing_consequence(tmp_path: Path) -> None:
    item = _image_model_item()
    del item["consequence"]
    art = _run(tmp_path, [item])
    assert _ledger_rows(art["ledger"]) == [], (
        "D-2 filing gate: candidates failing the wording triple are rejected, "
        "not filed"
    )
    assert art["report"]["ledger"]["rejected"], (
        "rejects-and-REPORTS: the rejection must be visible in the run report"
    )


def test_passes_wording_triple_helper() -> None:
    good = (
        "DOCUMENTED: docs list X (https://developers.gamma.app/reference/x.md, "
        "fetched 2026-07-02T00:00:00Z). OBSERVED: enum Y differs (app...._act:X). "
        "CONSEQUENCE: dispatch may 404."
    )
    assert audit.passes_wording_triple(good)
    assert not audit.passes_wording_triple("DOCUMENTED: x. OBSERVED: y.")
    assert not audit.passes_wording_triple("DOCUMENTED: x. CONSEQUENCE: z. no url")


def test_output_digest_recipe_is_pinned() -> None:
    """AC#5 as amended by review amendment P10 (ratified): output_digest =
    sha256 over (item_id, per-item normalized ANCHOR-scope text sha256
    [anchor_sha256], terminal_state, sorted diff) — canonical JSON, prefixed
    sha256:. Re-keyed off the whole-page content_sha256 so churn elsewhere on
    a shared page no longer re-files every item."""
    digest = audit.compute_output_digest(
        "enum-parity-image-model",
        "sha256:abc",
        "drift-detected",
        ["b", "a"],
    )
    expected_payload = json.dumps(
        {
            "anchor_sha256": "sha256:abc",
            "diff": ["a", "b"],
            "item_id": "enum-parity-image-model",
            "terminal_state": "drift-detected",
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    expected = "sha256:" + hashlib.sha256(expected_payload.encode("utf-8")).hexdigest()
    assert digest == expected


def test_unchanged_docs_rerun_is_ledger_noop(tmp_path: Path) -> None:
    """AC#5/A-5 + AC#11 hermetic twin: identical content -> 0 new lines,
    byte-identical ledger."""
    _seed_standing(tmp_path)
    art1 = _run(tmp_path, [_image_model_item(), _burst_429_item()])
    bytes_after_first = art1["ledger"].read_bytes()
    assert bytes_after_first, "first run must have written"

    manifest = art1["manifest"]
    with responses.RequestsMock(assert_all_requests_are_fired=False) as rsps:
        _serve_preflight(rsps)
        _serve(rsps, IMAGE_MODELS_URL)
        _serve(rsps, ASYNC_URL)
        exit2 = audit.run_audit(
            manifest_path=manifest,
            ledger_path=art1["ledger"],
            evidence_dir=tmp_path / "evidence-2",
            doc_sources_path=art1["doc_sources"],
            dry_run=False,
            fetch_interval_s=0.0,
        )
    assert exit2 == audit.EXIT_DRIFT
    assert art1["ledger"].read_bytes() == bytes_after_first, (
        "digest-idempotent: unchanged docs re-run is a ledger NO-OP"
    )


def test_shared_page_churn_outside_anchor_is_ledger_noop(tmp_path: Path) -> None:
    """P10 RED probe: the digest is keyed to the item's ANCHOR-scoped text —
    churn elsewhere on a shared page must NOT re-file the item."""
    art1 = _run(tmp_path, [_image_model_item()])
    bytes_after_first = art1["ledger"].read_bytes()
    assert bytes_after_first, "first run must have written"

    churned = (FIXTURE_DIR / "image_model_accepted_values.md").read_bytes() + (
        b"\n\nUnrelated footer churn appended OUTSIDE the anchored section.\n"
    )
    with responses.RequestsMock(assert_all_requests_are_fired=False) as rsps:
        _serve_preflight(rsps)
        rsps.get(IMAGE_MODELS_URL, body=churned)
        exit2 = audit.run_audit(
            manifest_path=art1["manifest"],
            ledger_path=art1["ledger"],
            evidence_dir=tmp_path / "evidence-2",
            doc_sources_path=art1["doc_sources"],
            dry_run=False,
            fetch_interval_s=0.0,
        )
    assert exit2 == audit.EXIT_DRIFT
    assert art1["ledger"].read_bytes() == bytes_after_first, (
        "whole-page churn outside the anchor re-filed the item (P10: digest "
        "must be keyed to anchor_sha256, not content_sha256)"
    )


def test_observation_field_discipline(tmp_path: Path) -> None:
    """D-3: real timestamps, evidence-dir birthing_run_ref, id shape (P10:
    ids carry an 8-hex digest suffix so same-day doc changes mint distinct ids)."""
    art = _run(tmp_path, [_image_model_item()])
    for obs in _ledger_rows(art["ledger"]):
        assert re.fullmatch(
            r"obs-gamma-[a-z0-9-]+-\d{4}-\d{2}-\d{2}-[0-9a-f]{8}",
            obs["observation_id"],
        ), obs
        assert obs["observation_id"].endswith(
            obs["output_digest"].removeprefix("sha256:")[:8]
        ), "id digest8 suffix must come from the observation's own output_digest"
        assert not obs["observed_at"].endswith("T00:00:00Z"), (
            "T00:00:00Z placeholders end with the grandfathered seeds (D-3)"
        )
        datetime.fromisoformat(obs["observed_at"].replace("Z", "+00:00"))
        ref = obs["birthing_run_ref"]
        assert not Path(ref).is_absolute(), "birthing_run_ref is repo-relative"
        assert "evidence" in ref
        assert obs["output_digest"].startswith("sha256:")


# ---------------------------------------------------------------------------
# Exit tiers (S-3) + pre-flight VOID (M-11 / W-5) + integrity
# ---------------------------------------------------------------------------


def test_exit_zero_when_all_confirmed(tmp_path: Path) -> None:
    art = _run(tmp_path, [_text_mode_item(), _burst_429_item()])
    assert art["exit"] == audit.EXIT_OK == 0


def test_exit_ten_on_drift(tmp_path: Path) -> None:
    art = _run(tmp_path, [_text_mode_item(), _image_model_item()])
    assert art["exit"] == audit.EXIT_DRIFT == 10


def test_exit_void_when_preflight_down_and_nothing_runs(tmp_path: Path) -> None:
    manifest = _write_manifest(tmp_path, [_text_mode_item()])
    ledger = tmp_path / "ledger.jsonl"
    doc_sources = tmp_path / "doc-sources.yaml"
    shutil.copyfile(DOC_SOURCES_PATH, doc_sources)
    before = doc_sources.read_bytes()
    with responses.RequestsMock() as rsps:
        _serve_preflight(rsps, ok=False)
        exit_code = audit.run_audit(
            manifest_path=manifest,
            ledger_path=ledger,
            evidence_dir=tmp_path / "evidence",
            doc_sources_path=doc_sources,
            dry_run=False,
            fetch_interval_s=0.0,
        )
        assert len(rsps.calls) == 1, (
            "VOID-before-start: no item page may be fetched after a failed "
            "pre-flight probe (M-11); ZERO mid-run retries"
        )
    assert exit_code == audit.EXIT_VOID == 20
    assert not ledger.exists() or ledger.read_bytes() == b""
    assert doc_sources.read_bytes() == before, "no last_refreshed stamp on a VOID run"


def test_exit_void_when_all_indeterminate(tmp_path: Path) -> None:
    """W-5 anti-vacuous floor: 'network down' must never read as 'no drift'.
    P3: a VOID run also never writes the ledger nor stamps doc-sources."""
    art = _run(tmp_path, [_text_mode_item(), _image_model_item()], serve_status=503)
    assert art["exit"] == audit.EXIT_VOID
    assert _ledger_rows(art["ledger"]) == [], "VOID run must not write (P1/P3)"
    assert art["doc_sources"].read_bytes() == DOC_SOURCES_PATH.read_bytes(), (
        "no last_refreshed stamp on an all-indeterminate VOID run (P3)"
    )


def test_probe_landing_confirmed_is_integrity_failure(tmp_path: Path) -> None:
    """A probe that CONFIRMS means the teeth are broken -> VOID, not a pass."""
    broken_probe = _probe_item(
        extraction={"anchor": "### Best practices"},
        expected_documented="Use 5-second polling intervals",
    )
    art = _run(tmp_path, [broken_probe, _text_mode_item()])
    assert art["exit"] == audit.EXIT_VOID
    assert _ledger_rows(art["ledger"]) == [], "probes never write, even broken ones"


def test_void_run_never_writes_ledger_or_stamps(tmp_path: Path) -> None:
    """P1 RED probe: integrity-failure VOID (broken probe CONFIRMS) alongside a
    real drift item — the exit tier is computed BEFORE the write phase; a VOID
    run writes NOTHING (no ledger rows, no doc-sources stamp) but the run
    report still records the would-have-written rows."""
    broken_probe = _probe_item(
        extraction={"anchor": "### Best practices"},
        expected_documented="Use 5-second polling intervals",
    )
    art = _run(tmp_path, [broken_probe, _image_model_item()])
    assert art["exit"] == audit.EXIT_VOID
    assert _ledger_rows(art["ledger"]) == [], (
        "a VOID run wrote ledger rows (P1: integrity/VOID write-gate)"
    )
    assert art["doc_sources"].read_bytes() == DOC_SOURCES_PATH.read_bytes(), (
        "a VOID run stamped doc-sources last_refreshed (P1/P3)"
    )
    assert art["report"]["integrity_failure"] is True
    assert art["report"]["ledger"]["would_write"], (
        "the VOID report must still record the would-have-written rows (P1)"
    )


def test_compute_exit_tier_excludes_probe_and_findings_only() -> None:
    """P6 (ratified spec amendment): probe + findings_only items are excluded
    from tier aggregation — the probe participates ONLY via the integrity
    check; findings-only items are report-only. Real items alone drive tiers."""

    def _r(state: str, *, probe: bool = False, findings: bool = False) -> dict[str, Any]:
        return {"terminal_state": state, "probe": probe, "findings_only": findings}

    assert audit.compute_exit_tier(
        [_r("drift-detected", probe=True), _r("drift-detected", findings=True), _r("confirmed")],
        preflight_ok=True,
    ) == audit.EXIT_OK
    assert audit.compute_exit_tier(
        [_r("indeterminate"), _r("drift-detected")], preflight_ok=True
    ) == audit.EXIT_DRIFT
    assert audit.compute_exit_tier(
        [_r("confirmed"), _r("indeterminate")], preflight_ok=True
    ) == audit.EXIT_VOID, "partial-uncertified (no drift) is VOID"
    assert audit.compute_exit_tier(
        [_r("drift-detected", probe=True)], preflight_ok=True
    ) == audit.EXIT_VOID, "a run with ZERO real items certifies nothing"
    assert audit.compute_exit_tier(
        [_r("confirmed")], preflight_ok=True, integrity_failure=True
    ) == audit.EXIT_VOID


def test_exit_zero_when_probe_and_findings_drift_but_real_confirmed(
    tmp_path: Path,
) -> None:
    """P6 RED probe (healthy manifest): the probe drifts AS DESIGNED and a
    findings-only item drifts (report-only) — with every real item confirmed
    the run exits 0."""
    tags_item = {
        "item_id": "finding-imageoptions-discrete-tags-field",
        "kind": "doc-fact",
        "expected_documented": "imageOptions.tags",
        "doc_url": PARAMS_URL,
        "comparator": "literal-presence",
        "extraction": {"anchor": "#### imageOptions", "until": "#### cardOptions"},
        "findings_only": True,
        "consequence": "answers the keywords-routing field-surface question (J-7); evidence only.",
    }
    art = _run(tmp_path, [_probe_item(), tags_item, _text_mode_item()])
    states = {i["item_id"]: i["terminal_state"] for i in art["report"]["items"]}
    assert states["probe-absent-anchor-teeth"] == "drift-detected"
    assert states["finding-imageoptions-discrete-tags-field"] == "drift-detected"
    assert states["enum-parity-text-mode"] == "confirmed"
    assert art["exit"] == audit.EXIT_OK, (
        "a healthy run (probe drifting as designed, findings-only drift, all "
        "real items confirmed) must exit 0 (P6)"
    )


def test_exit_void_on_partial_outage_even_with_probe_drift(tmp_path: Path) -> None:
    """P6 RED probe (partial outage): real items indeterminate while the probe
    drifted — probe drift must not mask an uncertified run; exit 20."""
    art = _run(
        tmp_path,
        [_probe_item(), _text_mode_item()],
        status_by_url={PARAMS_URL: 503},
    )
    states = {i["item_id"]: i["terminal_state"] for i in art["report"]["items"]}
    assert states["probe-absent-anchor-teeth"] == "drift-detected"
    assert states["enum-parity-text-mode"] == "indeterminate"
    assert art["exit"] == audit.EXIT_VOID, (
        "probe drift masked an all-real-items-indeterminate outage as tier 10 (P6)"
    )


def test_corrupt_ledger_precheck_voids_with_report(tmp_path: Path) -> None:
    """P4 RED probe: an unparseable existing ledger is detected right after
    preflight — run-report written, EXIT_VOID, no traceback, ledger untouched."""
    ledger = tmp_path / "ledger.jsonl"
    corrupt = '{"observation_id": "ok", "output_digest": "sha256:x"}\n{ not json\n'
    ledger.write_text(corrupt, encoding="utf-8")
    art = _run(tmp_path, [_image_model_item()])
    assert art["exit"] == audit.EXIT_VOID
    assert art["report"] is not None, "run report must land even on precheck VOID"
    assert art["report"]["ledger"].get("precheck_error"), art["report"]["ledger"]
    assert ledger.read_text(encoding="utf-8") == corrupt, (
        "the corrupt ledger must be left byte-identical for forensics"
    )


def test_write_phase_exception_lands_report_and_void(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """P4 RED probe: an unexpected write-phase exception must land report+20,
    never a bare traceback / exit 1."""

    def _boom(ledger_path: Any, observation: dict[str, Any]) -> bool:
        raise RuntimeError("disk gone mid-write")

    monkeypatch.setattr(audit, "append_observation", _boom)
    art = _run(tmp_path, [_image_model_item()])
    assert art["exit"] == audit.EXIT_VOID
    assert art["report"] is not None
    assert "disk gone mid-write" in str(
        art["report"]["ledger"].get("write_phase_error")
    ), art["report"]["ledger"]
    assert art["doc_sources"].read_bytes() == DOC_SOURCES_PATH.read_bytes(), (
        "no doc-sources stamp after a write-phase failure"
    )


def test_preflight_empty_body_is_void_before_start(tmp_path: Path) -> None:
    """N1: a 200 llms.txt with an EMPTY body is not a passing preflight — the
    doc surface is not serving; VOID before any item fetch."""
    manifest = _write_manifest(tmp_path, [_text_mode_item()])
    ledger = tmp_path / "ledger.jsonl"
    doc_sources = tmp_path / "doc-sources.yaml"
    shutil.copyfile(DOC_SOURCES_PATH, doc_sources)
    with responses.RequestsMock(assert_all_requests_are_fired=False) as rsps:
        rsps.get(PREFLIGHT_URL, body=b"")
        exit_code = audit.run_audit(
            manifest_path=manifest,
            ledger_path=ledger,
            evidence_dir=tmp_path / "evidence",
            doc_sources_path=doc_sources,
            dry_run=False,
            fetch_interval_s=0.0,
        )
        assert len(rsps.calls) == 1, "no item fetch after an empty-body preflight"
    assert exit_code == audit.EXIT_VOID


# ---------------------------------------------------------------------------
# AC#4 driver surface: dry-run, ledger default, stamping, report receipts
# ---------------------------------------------------------------------------


def test_default_ledger_path_is_the_real_ssot() -> None:
    from app.specialists.gary.learned_dependencies import (
        GAMMA_LEARNED_OBSERVATIONS_PATH,
    )

    assert Path(audit.DEFAULT_LEDGER_PATH) == Path(GAMMA_LEARNED_OBSERVATIONS_PATH)


def test_dry_run_reports_without_writing(tmp_path: Path) -> None:
    art = _run(tmp_path, [_image_model_item()], dry_run=True)
    assert art["exit"] == audit.EXIT_DRIFT, "classification/report semantics unchanged"
    assert not art["ledger"].exists() or art["ledger"].read_bytes() == b""
    assert art["report"] is not None and art["report"]["dry_run"] is True
    assert art["report"]["ledger"]["would_write"], (
        "dry-run must still REPORT what it would have filed"
    )
    original = DOC_SOURCES_PATH.read_bytes()
    assert art["doc_sources"].read_bytes() == original, "no stamping under --dry-run"


def test_run_stamps_doc_sources_last_refreshed_only(tmp_path: Path) -> None:
    art = _run(tmp_path, [_text_mode_item()])
    before_lines = DOC_SOURCES_PATH.read_text(encoding="utf-8").splitlines()
    after_lines = art["doc_sources"].read_text(encoding="utf-8").splitlines()
    assert len(before_lines) == len(after_lines)
    diff = [
        (a, b) for a, b in zip(before_lines, after_lines, strict=True) if a != b
    ]
    assert len(diff) == 1, f"only the last_refreshed line may change; diff={diff}"
    assert diff[0][0].startswith("last_refreshed:")
    assert diff[0][1].startswith("last_refreshed:") and "2" in diff[0][1]


def test_report_carries_per_item_receipts_and_ledger_digests(tmp_path: Path) -> None:
    art = _run(tmp_path, [_text_mode_item(), _image_model_item(), _probe_item()])
    report = art["report"]
    assert report["exit_tier"] == art["exit"]
    assert set(report["terminal_state_counts"]) <= {
        "confirmed",
        "drift-detected",
        "indeterminate",
    }
    assert sum(report["terminal_state_counts"].values()) == 3, (
        "every item reaches exactly one terminal state (totality)"
    )
    for item in report["items"]:
        receipt = item["receipt"]
        assert receipt["final_url"].startswith("https://developers.gamma.app/")
        assert "http_status" in receipt
        assert "fetched_at" in receipt
        assert "content_sha256" in receipt
        assert "anchor_sha256" in receipt
    ledger_block = report["ledger"]
    for key in ("before_lines", "after_lines", "before_sha256", "after_sha256"):
        assert key in ledger_block
    # Human-readable table also lands in the evidence dir.
    assert (art["evidence"] / "run-report.md").exists()


def test_run_report_md_escapes_pipes_in_table_cells(tmp_path: Path) -> None:
    """N5: a '|' inside a cell (e.g. an anchor repr in a doc-restructure
    reason) must be escaped or the markdown table shreds."""
    item = _text_mode_item(
        item_id="enum-parity-pipe-anchor",
        extraction={"anchor": "#### |piped|anchor|", "collect": "inline-code"},
    )
    art = _run(tmp_path, [item])
    md = (art["evidence"] / "run-report.md").read_text(encoding="utf-8")
    table_rows = [
        line for line in md.splitlines()
        if line.startswith("|") and "item_id" not in line and "---" not in line
    ]
    assert table_rows, "run-report.md must carry the per-item table"
    for line in table_rows:
        unescaped = len(re.findall(r"(?<!\\)\|", line))
        assert unescaped == 6, f"table row shredded by unescaped pipes: {line!r}"


def test_stamp_doc_sources_preserves_line_ending_convention(tmp_path: Path) -> None:
    """N6: stamping keeps the file's original newline convention byte-for-byte."""
    crlf = tmp_path / "ds-crlf.yaml"
    crlf.write_bytes(b'last_refreshed: "old"\r\nother: 1\r\n')
    audit.stamp_doc_sources(crlf, "2026-07-02T00:00:00Z")
    raw = crlf.read_bytes()
    assert b'last_refreshed: "2026-07-02T00:00:00Z"\r\n' in raw, raw
    assert b"other: 1\r\n" in raw

    lf = tmp_path / "ds-lf.yaml"
    lf.write_bytes(b'last_refreshed: "old"\nother: 1\n')
    audit.stamp_doc_sources(lf, "2026-07-02T00:00:00Z")
    raw_lf = lf.read_bytes()
    assert b"\r" not in raw_lf
    assert b'last_refreshed: "2026-07-02T00:00:00Z"\n' in raw_lf


def test_main_manifest_error_exits_void_without_traceback(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """N8: a malformed manifest through the CLI is a loud stderr message +
    exit 20 — never a bare ManifestError traceback."""
    bad = tmp_path / "bad-manifest.yaml"
    bad.write_text("schema_version: '1.0'\nitems: []\n", encoding="utf-8")
    rc = audit.main(
        [
            "--manifest", str(bad),
            "--ledger-path", str(tmp_path / "ledger.jsonl"),
            "--evidence-dir", str(tmp_path / "evidence"),
            "--dry-run",
        ]
    )
    assert rc == audit.EXIT_VOID
    err = capsys.readouterr().err
    assert "manifest" in err.lower(), err


def test_relative_evidence_ref_fails_loud_outside_repo() -> None:
    """N9: birthing_run_ref is repo-relative BY CONTRACT — an out-of-repo
    evidence dir is a configuration error, not a silent absolute path."""
    outside = Path("C:/Windows/Temp/leg-e-nowhere-evidence")
    with pytest.raises(ValueError, match="repo"):
        audit._relative_evidence_ref(outside)


# ---------------------------------------------------------------------------
# AC#6 / D-4 — lock immunity + candidate-only + invisible to apply_learned_rules
# ---------------------------------------------------------------------------


def test_lock_immunity_candidate_only_and_rule_invisibility(tmp_path: Path) -> None:
    lock_before = LOCK_PATH.read_bytes()
    art = _run(tmp_path, [_image_model_item(), _burst_429_item()])
    assert LOCK_PATH.read_bytes() == lock_before, (
        "gamma-learned-rules.lock stays byte-identical through Leg-E (D-4)"
    )
    rows = _ledger_rows(art["ledger"])
    assert rows and all(obs["status"] == "candidate" for obs in rows)

    from app.specialists.gary.learned_dependencies import apply_learned_rules

    errors, warnings = apply_learned_rules(
        {}, {"image_model": "recraft-v3-svg", "image_source": "pexels"}, rows
    )
    assert errors == [] and warnings == [], (
        "nothing Leg-E writes may be visible to apply_learned_rules "
        "(observation != rule, Murat M-10)"
    )
