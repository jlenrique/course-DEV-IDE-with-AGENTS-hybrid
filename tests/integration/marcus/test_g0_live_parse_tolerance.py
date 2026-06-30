"""RED-first reliability spec — tolerant parse of the live G0 pre-pass response.

Found LIVE (2026-06-29 tejal trial, real gpt-5): the keystone Marcus-SPOC
component-extraction pre-pass crashed the whole production walk at G0E with
``json.decoder.JSONDecodeError: Invalid control character at: line 225 column
124`` — gpt-5 returned a large JSON object containing a LITERAL control character
(an unescaped newline/tab) INSIDE a string value, which strict ``json.loads``
rejects, before any gate.

These specs pin the tolerant parse (mirrors the proven
``coverage_annotation.extract_coverage_rows`` /
``pedagogy_annotation._extract_pedagogy_rows`` pattern + the targeted
``strict=False`` fix) and the fail-loud contract on a truly-unparseable response
(a CLEAR domain error, never a bare ``JSONDecodeError``, never a silent ``{}``).
"""

from __future__ import annotations

import json

import pytest

from app.marcus.orchestrator import g0_enrichment_wiring as gw


# --------------------------------------------------------------------------- #
# The targeted crash: a literal control character INSIDE a string value.       #
# --------------------------------------------------------------------------- #
def test_parses_control_character_inside_string_value() -> None:
    # A realistic gpt-5 component-extraction response with an UNESCAPED newline
    # inside an excerpt string value — strict json.loads raises here (the live
    # crash); the tolerant helper must parse it (strict=False).
    raw = '{"components": [{"excerpt": "line1\nline2", "type": "slide"}]}'
    # Sanity: this IS the defect class — strict parsing raises today.
    with pytest.raises(json.JSONDecodeError):
        json.loads(raw)
    payload = gw._parse_live_extraction_response(raw)
    assert isinstance(payload, dict)
    assert payload["components"][0]["excerpt"] == "line1\nline2"


def test_parses_fenced_control_char_response() -> None:
    # Same control-char defect, wrapped in a ```json fence (prose-framed output).
    raw = '```json\n{"components": [{"excerpt": "alpha\tbeta"}]}\n```'
    payload = gw._parse_live_extraction_response(raw)
    assert isinstance(payload, dict)
    assert payload["components"][0]["excerpt"] == "alpha\tbeta"


def test_parses_content_block_list_with_control_char() -> None:
    # response.content as a content-block list (some adapters) + a control char.
    content = [{"type": "text", "text": '{"components": [{"excerpt": "x\x0by"}]}'}]
    payload = gw._parse_live_extraction_response(content)
    assert payload["components"][0]["excerpt"] == "x\x0by"


def test_parses_first_brace_span_when_wrapped_in_prose() -> None:
    raw = 'Here is the extraction:\n{"components": [{"excerpt": "ok\nnow"}]} -- done.'
    payload = gw._parse_live_extraction_response(raw)
    assert payload["components"][0]["excerpt"] == "ok\nnow"


# --------------------------------------------------------------------------- #
# Fail-loud contract: unparseable / empty → CLEAR domain error, never silent.  #
# --------------------------------------------------------------------------- #
def test_unparseable_response_raises_clear_domain_error() -> None:
    raw = "this is not json at all, and has no closing brace { oops"
    with pytest.raises(gw.G0EnrichmentParseError) as exc_info:
        gw._parse_live_extraction_response(raw)
    # NOT a bare JSONDecodeError leaking out, and a useful, contextful message.
    assert not isinstance(exc_info.value, json.JSONDecodeError)
    msg = str(exc_info.value)
    assert "strict=False" in msg
    assert "oops" in msg  # snippet of the offending text is surfaced


def test_empty_response_raises_clear_domain_error_not_silent() -> None:
    # An empty live pre-pass is a BROKEN keystone extraction — fail loud, never
    # silently return {} (which would hide the breakage downstream).
    with pytest.raises(gw.G0EnrichmentParseError):
        gw._parse_live_extraction_response("")
    with pytest.raises(gw.G0EnrichmentParseError):
        gw._parse_live_extraction_response("   \n  ")


def test_g0_enrichment_parse_error_is_value_error() -> None:
    # Subclasses ValueError so existing `except (ValueError, TypeError)` guards
    # can catch it, but it is a DISTINCT, named domain error (clear at the top).
    assert issubclass(gw.G0EnrichmentParseError, ValueError)
