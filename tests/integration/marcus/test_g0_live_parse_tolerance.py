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
import logging
from pathlib import Path
from types import SimpleNamespace

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


# --------------------------------------------------------------------------- #
# TRUNCATION salvage: a valid JSON PREFIX cut off mid-structure (gpt-5 hit its  #
# output-token ceiling). Found LIVE 2026-06-29: JSONDecodeError "Expecting ','  #
# delimiter: line 196 column 8". Recover the longest complete-object prefix.    #
# --------------------------------------------------------------------------- #
_TRUNCATED_COMPONENTS = (
    '{"components": [\n'
    '  {"parent_source_id": "s1", "type": "slide", "excerpt": "first"},\n'
    '  {"parent_source_id": "s1", "type": "slide", "excerpt": "second"},\n'
    '  {"parent_source_id": "s1", "type": "sl'
)


def test_truncated_components_array_raises_today_then_salvages() -> None:
    # Sanity: the truncated prefix is NOT parseable by strict OR tolerant full parse
    # (this is the live crash class — a well-formed prefix cut mid-final-object).
    with pytest.raises(json.JSONDecodeError):
        json.loads(_TRUNCATED_COMPONENTS)
    # After Fix B the tolerant helper SALVAGES the complete-object prefix.
    payload = gw._parse_live_extraction_response(_TRUNCATED_COMPONENTS)
    assert isinstance(payload, dict)
    assert len(payload["components"]) == 2  # 2 complete; trailing partial discarded
    assert payload["components"][0]["excerpt"] == "first"
    assert payload["components"][1]["excerpt"] == "second"


def test_truncation_salvage_is_loud(caplog: pytest.LogCaptureFixture) -> None:
    # LOUD never silent: a truncated salvage MUST log a WARNING that surfaces the
    # truncation + the recovered count (a PARTIAL extraction is never treated as complete).
    with caplog.at_level(logging.WARNING, logger="app.marcus.orchestrator.g0_enrichment_wiring"):
        payload = gw._parse_live_extraction_response(_TRUNCATED_COMPONENTS)
    warned = "\n".join(r.getMessage() for r in caplog.records if r.levelno >= logging.WARNING)
    assert "TRUNCAT" in warned.upper()
    assert "2" in warned  # recovered-count surfaced
    # provenance flag stamped on the payload so downstream can see it was partial
    assert payload.get("_g0_extraction_truncated") is True
    assert payload.get("_g0_extraction_recovered_components") == 2


def test_truncated_salvage_also_recovers_learning_objectives() -> None:
    raw = (
        '{"learning_objectives": [{"id": "lo1", "text": "alpha"}, {"id": "lo2", "text": "beta"}], '
        '"components": [{"parent_source_id": "s1", "excerpt": "one"}, '
        '{"parent_source_id": "s1", "excerpt": "tw'
    )
    payload = gw._parse_live_extraction_response(raw)
    assert len(payload["components"]) == 1
    assert len(payload["learning_objectives"]) == 2


def test_salvage_recovering_zero_complete_objects_raises_clear_error() -> None:
    # A truncation so severe the FIRST component object is itself incomplete →
    # zero complete objects recovered → total failure, raise the clear domain error.
    raw = '{"components": [\n  {"parent_source_id": "s1", "type": "sl'
    with pytest.raises(gw.G0EnrichmentParseError):
        gw._parse_live_extraction_response(raw)


# --------------------------------------------------------------------------- #
# Fix A: the None-fallback chat-model factory binds a GENEROUS output budget so #
# the keystone extraction does not truncate (root cause of the live crash).     #
# --------------------------------------------------------------------------- #
def test_default_extraction_factory_binds_generous_budget_and_timeout() -> None:
    handle = gw._default_extraction_chat_factory()("marcus")
    assert handle.chat.max_tokens == gw.G0_EXTRACTION_MAX_COMPLETION_TOKENS
    assert gw.G0_EXTRACTION_MAX_COMPLETION_TOKENS >= 32000
    assert handle.chat.request_timeout == gw.G0_EXTRACTION_REQUEST_TIMEOUT_S
    # max_retries=2 absorbs gpt-5's per-call latency variance (a timed-out attempt
    # retries into a faster response); each attempt stays hard-bounded by the timeout.
    assert handle.chat.max_retries == 2


# --------------------------------------------------------------------------- #
# Fix B: REQUIRED-OUTPUT VALIDATION RETRY. A NON-EMPTY corpus that yields ZERO   #
# usable provisional LOs is an INVALID G0 response — the live call is re-issued   #
# ONCE, and a still-empty retry FAILS LOUD at G0 (never cascades to the cryptic   #
# 07W.1 deep-dive Promise error). Root cause: trial 4614f21f authored 0 LOs from  #
# 11 source files (with 25 typed components) and limped silently downstream.      #
# --------------------------------------------------------------------------- #
class _FakeChat:
    """A fake chat model whose ``invoke`` replays queued response contents in order."""

    def __init__(self, contents: list[str]) -> None:
        self._contents = list(contents)
        self.calls = 0

    def invoke(self, _messages: object) -> SimpleNamespace:
        self.calls += 1
        return SimpleNamespace(content=self._contents.pop(0))


def _factory(contents: list[str]) -> tuple[object, _FakeChat]:
    """Return a ``(chat_model_factory, fake_chat)`` pair driving ``_live_pre_pass``."""
    chat = _FakeChat(contents)
    handle = SimpleNamespace(chat=chat)
    return (lambda _model_id: handle), chat


def _two_file_corpus(tmp_path: Path) -> list[tuple[str, Path]]:
    (tmp_path / "a.md").write_text("# File A\nAlpha teaches leadership basics.\n", encoding="utf-8")
    (tmp_path / "b.md").write_text("# File B\nBeta teaches teamwork basics.\n", encoding="utf-8")
    return gw._enumerate(tmp_path)


def _components(enumerated: list[tuple[str, Path]]) -> list[dict[str, object]]:
    return [
        {
            "parent_source_id": sid,
            "type": "slide",
            "label": "S",
            "locator": "File",
            "excerpt": "teaches",
        }
        for sid, _ in enumerated
    ]


def _payload_zero_los(enumerated: list[tuple[str, Path]]) -> str:
    # A well-formed response with typed components but an EMPTY provisional_los array —
    # the exact 4614f21f shape (components present, zero LOs).
    return json.dumps({"components": _components(enumerated), "provisional_los": []})


def _payload_with_los(enumerated: list[tuple[str, Path]]) -> str:
    return json.dumps(
        {
            "components": _components(enumerated),
            "provisional_los": [
                {
                    "objective_id": f"lo-g0-{i:03d}",
                    "statement": f"Learner can explain the concept grounded in {sid}.",
                    "confidence": "low",
                    "source_refs": [
                        {"source_id": sid, "locator": "File", "quoted_span": "teaches"}
                    ],
                }
                for i, (sid, _) in enumerate(enumerated, start=1)
            ],
        }
    )


def test_zero_los_from_nonempty_corpus_retries_once_then_fails_loud(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    enumerated = _two_file_corpus(tmp_path)
    factory, chat = _factory([_payload_zero_los(enumerated), _payload_zero_los(enumerated)])
    with caplog.at_level(logging.WARNING), pytest.raises(gw.G0EnrichmentParseError) as exc_info:
        gw._live_pre_pass(enumerated, tmp_path, factory)
    # The live G0 call is re-issued EXACTLY once (required-output retry, not a re-run).
    assert chat.calls == 2
    # The retry is LOUD (operator sees the 0-LO invalidity + retry decision).
    assert any("0 provisional learning objectives" in r.message for r in caplog.records)
    # The fail-loud names the REAL problem (0 LOs from N source files), not 07W.1.
    msg = str(exc_info.value)
    assert "0 learning objectives" in msg
    assert f"{len(enumerated)} source" in msg


def test_zero_los_then_nonzero_on_retry_succeeds(tmp_path: Path) -> None:
    enumerated = _two_file_corpus(tmp_path)
    factory, chat = _factory([_payload_zero_los(enumerated), _payload_with_los(enumerated)])
    typed, los, provenance = gw._live_pre_pass(enumerated, tmp_path, factory)
    # Retried once, then the non-empty response is accepted — no fail-loud.
    assert chat.calls == 2
    assert len(los) == len(enumerated)
    assert typed, "the extracted components survive the required-output retry"
    assert len(provenance) == len(enumerated)


def test_nonzero_los_first_pass_does_not_retry(tmp_path: Path) -> None:
    enumerated = _two_file_corpus(tmp_path)
    factory, chat = _factory([_payload_with_los(enumerated)])
    typed, los, provenance = gw._live_pre_pass(enumerated, tmp_path, factory)
    # A valid first response must NOT trigger the required-output retry (preserve behavior).
    assert chat.calls == 1
    assert len(los) == len(enumerated)


def test_empty_live_response_still_fails_loud_before_any_retry(tmp_path: Path) -> None:
    # An empty RESPONSE TEXT fails loud on the FIRST dispatch (the pre-existing guard) —
    # the new 0-LO retry must NOT swallow or defer it.
    enumerated = _two_file_corpus(tmp_path)
    factory, chat = _factory([""])
    with pytest.raises(gw.G0EnrichmentParseError):
        gw._live_pre_pass(enumerated, tmp_path, factory)
    assert chat.calls == 1
