from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from app.marcus.lesson_plan import pass1_call_journal as journal_module
from app.marcus.lesson_plan.pass1_call_journal import (
    Pass1CallJournalError,
    begin_or_resume_pass1_call,
    build_pass1_call_identity,
    record_pass1_candidate_processing,
    record_pass1_dispatch_exception,
    record_pass1_response,
)
from app.marcus.lesson_plan.pass1_call_journal import (
    complete_pass1_call as _complete_pass1_call,
)
from app.models.state.cache_state import CacheState
from app.models.state.run_state import RunState
from app.specialists.irene_pass1 import _act as pass1_act
from tests._helpers.pass1_bundle import write_primary_slide_bundle
from tests._helpers.pass1_catalog_response import select_catalog_ids

EXACT = "We can no longer rely on static training."
JOURNAL_GLOB = "irene-pass1-call-*.v1.json"


def _state(payload: dict[str, Any], *, entries_count: int = 0) -> RunState:
    return RunState(
        graph_version="v0.1-stub",
        temperature=0.0,
        cache_state=CacheState(
            cache_prefix=json.dumps(payload, sort_keys=True),
            entries_count=entries_count,
        ),
    )


def _payload(tmp_path: Path, run_id: str) -> dict[str, Any]:
    bundle = tmp_path / f"{run_id}-bundle"
    bundle.mkdir()
    write_primary_slide_bundle(bundle, f"# Corpus\n\n{EXACT}")
    return {
        "mode": "pass-1",
        "run_id": run_id,
        "runs_root": str(tmp_path),
        "bundle_reference": str(bundle),
        "manifest_node_id": "04A",
    }


def _legacy_candidate(anchor: str = EXACT) -> str:
    return json.dumps(
        {
            "lesson_summary": "Summary",
            "plan_units": [
                {
                    "unit_id": "u01",
                    "title": "Adaptive practice",
                    "learning_objective": "Explain adaptive practice.",
                    "scope_decision": "in-scope",
                    "source_refs": [anchor],
                    "rationale": "The source establishes the need.",
                    "cluster_id": "c-u01",
                    "cluster_role": "head",
                    "cluster_position": "establish",
                    "narrative_arc": "Static knowledge to adaptive practice",
                    "cluster_interstitial_count": 0,
                    "fidelity": "creative",
                }
            ],
            "collateral": {"declaration": "none"},
        }
    )


@dataclass
class _InspectingChat:
    run_dir: Path
    raw: str
    calls: int = 0
    observed_pre_dispatch: dict[str, Any] | None = None

    def invoke(self, messages: list[dict[str, str]]) -> SimpleNamespace:
        self.calls += 1
        journals = list(self.run_dir.glob(JOURNAL_GLOB))
        assert len(journals) == 1
        self.observed_pre_dispatch = json.loads(journals[0].read_text(encoding="utf-8"))
        assert self.observed_pre_dispatch["state"] == "call_in_progress"
        assert (
            self.observed_pre_dispatch["processor_version"]
            == journal_module.PROCESSOR_VERSION
        )
        identity_body = {
            key: self.observed_pre_dispatch[key]
            for key in journal_module._IDENTITY_KEYS  # noqa: SLF001
            if key != "request_digest"
        }
        assert self.observed_pre_dispatch["request_digest"] == journal_module._digest(  # noqa: SLF001
            identity_body
        )
        raw = self.raw
        try:
            json.loads(raw)
        except json.JSONDecodeError:
            try:
                json.loads(raw[:-1])
            except json.JSONDecodeError:
                pass
            else:
                raw = select_catalog_ids(raw[:-1], messages) + "}"
        else:
            raw = select_catalog_ids(raw, messages)
        return SimpleNamespace(
            content=raw,
            usage_metadata={"input_tokens": 21, "output_tokens": 13},
            response_metadata={"model_name": "gpt-test", "finish_reason": "stop"},
            id="provider-response-1",
        )


@dataclass
class _InspectingHandle:
    chat: _InspectingChat
    model_config_digest: str = "sha256:" + "a" * 64


class _BombChat:
    def invoke(self, _messages: object) -> object:
        raise AssertionError("provider must not be recalled")


def _journal(run_dir: Path) -> tuple[Path, dict[str, Any]]:
    journals = list(run_dir.glob(JOURNAL_GLOB))
    assert len(journals) == 1
    return journals[0], json.loads(journals[0].read_text(encoding="utf-8"))


def complete_pass1_call(
    *,
    path: Path,
    identity: dict[str, Any],
    result_identity: dict[str, Any],
    result: dict[str, Any],
) -> None:
    """Prepare the legal v2 barrier for completion-semantic unit tests."""
    journal = json.loads(path.read_text(encoding="utf-8"))
    if journal.get("state") == "response_received":
        candidate = json.loads(journal["raw_response"])
        record_pass1_candidate_processing(
            path=path,
            identity=identity,
            action="strict-json",
            framing="plain",
            removed_byte=None,
            removed_offset=None,
            processed_candidate=candidate,
        )
    _complete_pass1_call(
        path=path,
        identity=identity,
        result_identity=result_identity,
        result=result,
    )


def test_predispatch_is_durable_and_completed_call_replays_without_provider(
    tmp_path: Path,
) -> None:
    run_id = "journal-complete-replay"
    payload = _payload(tmp_path, run_id)
    chat = _InspectingChat(tmp_path / run_id, _legacy_candidate())
    first = pass1_act.act(
        _state(payload),
        handle=_InspectingHandle(chat),
        model_id="gpt-test",
    )

    assert chat.calls == 1
    assert chat.observed_pre_dispatch is not None
    path, completed = _journal(tmp_path / run_id)
    assert completed["state"] == "completed"
    assert completed["raw_response_digest"].startswith("sha256:")
    assert completed["provider_evidence"]["usage_metadata"] == {
        "input_tokens": 21,
        "output_tokens": 13,
    }
    assert completed["result_identity"]["authority_digest"].startswith("sha256:")
    assert path.is_file()

    stored_output = json.loads(first["cache_state"]["cache_prefix"])
    Path(stored_output["artifact_path"]).unlink()
    Path(stored_output["plan_authority_receipt_path"]).unlink()

    replay = pass1_act.act(
        _state(payload),
        handle=SimpleNamespace(chat=_BombChat(), model_config_digest="sha256:" + "a" * 64),
        model_id="gpt-test",
    )
    assert replay == first
    assert Path(stored_output["artifact_path"]).is_file()
    assert Path(stored_output["plan_authority_receipt_path"]).is_file()


def test_v2_surplus_brace_processing_is_bound_and_replays_without_provider(
    tmp_path: Path,
) -> None:
    run_id = "journal-v2-surplus-brace"
    payload = _payload(tmp_path, run_id)
    chat = _InspectingChat(tmp_path / run_id, _legacy_candidate() + "}")

    first = pass1_act.act(
        _state(payload), handle=_InspectingHandle(chat), model_id="gpt-test"
    )
    assert chat.calls == 1
    _path, completed = _journal(tmp_path / run_id)
    receipt = completed["response_processing"]
    assert completed["state"] == "completed"
    assert receipt["journal_processor_version"] == journal_module.PROCESSOR_VERSION
    assert receipt["executed_processor_version"] == journal_module.PROCESSOR_VERSION
    assert receipt["action"] == "drop-one-surplus-final-rbrace"
    assert receipt["removed_byte"] == "}"
    assert receipt["removed_offset"] == len(completed["raw_response"]) - 1
    assert receipt["raw_response_digest"] == completed["raw_response_digest"]

    replay = pass1_act.act(
        _state(payload),
        handle=SimpleNamespace(
            chat=_BombChat(), model_config_digest="sha256:" + "a" * 64
        ),
        model_id="gpt-test",
    )
    assert replay == first


def test_v2_processing_receipt_is_idempotent_and_tamper_evident(tmp_path: Path) -> None:
    identity = _identity(run_id="journal-processing-receipt")
    resume = begin_or_resume_pass1_call(run_dir=tmp_path, identity=identity)
    record_pass1_response(
        path=resume.path,
        identity=identity,
        raw_response='{"plan_units":[]}}',
        provider_evidence={"usage_metadata": None},
    )
    candidate = {"plan_units": []}
    first = record_pass1_candidate_processing(
        path=resume.path,
        identity=identity,
        action="drop-one-surplus-final-rbrace",
        framing="plain",
        removed_byte="}",
        removed_offset=len('{"plan_units":[]}'),
        processed_candidate=candidate,
    )
    second = record_pass1_candidate_processing(
        path=resume.path,
        identity=identity,
        action="drop-one-surplus-final-rbrace",
        framing="plain",
        removed_byte="}",
        removed_offset=len('{"plan_units":[]}'),
        processed_candidate=candidate,
    )
    assert second == first

    journal = json.loads(resume.path.read_text(encoding="utf-8"))
    journal["response_processing"]["removed_offset"] -= 1
    journal["response_processing_digest"] = journal_module._digest(  # noqa: SLF001
        journal["response_processing"]
    )
    resume.path.write_text(json.dumps(journal), encoding="utf-8")
    with pytest.raises(Pass1CallJournalError, match="processing binding"):
        begin_or_resume_pass1_call(run_dir=tmp_path, identity=identity)


def test_v2_completion_cannot_mint_a_late_processing_receipt(tmp_path: Path) -> None:
    identity = _identity(run_id="journal-processing-barrier")
    resume = begin_or_resume_pass1_call(run_dir=tmp_path, identity=identity)
    record_pass1_response(
        path=resume.path,
        identity=identity,
        raw_response="{}",
        provider_evidence={"usage_metadata": None},
    )

    with pytest.raises(Pass1CallJournalError, match="no returned response"):
        _complete_pass1_call(
            path=resume.path,
            identity=identity,
            result_identity={},
            result={},
        )
    retained = json.loads(resume.path.read_text(encoding="utf-8"))
    assert retained["state"] == "response_received"
    assert "response_processing" not in retained


def test_v2_removed_offset_addresses_raw_utf8_bytes_across_framing(
    tmp_path: Path,
) -> None:
    candidate = {"lesson_summary": "Café", "plan_units": []}
    body = json.dumps(candidate, ensure_ascii=False) + "\n  }"
    raw_values = [f"  {body}\r\n", f" \n```json\n{body}\n```\t"]

    for index, raw in enumerate(raw_values):
        identity = _identity(run_id=f"journal-raw-byte-offset-{index}")
        resume = begin_or_resume_pass1_call(
            run_dir=tmp_path / str(index), identity=identity
        )
        record_pass1_response(
            path=resume.path,
            identity=identity,
            raw_response=raw,
            provider_evidence={"usage_metadata": None},
        )
        decoded, processing = pass1_act._decode_pass1_response_v2(raw)  # noqa: SLF001
        receipt = record_pass1_candidate_processing(
            path=resume.path,
            identity=identity,
            action=processing["action"],
            framing=processing["framing"],
            removed_byte=processing["removed_byte"],
            removed_offset=processing["removed_offset"],
            processed_candidate=decoded,
        )
        offset = receipt["removed_offset"]
        assert receipt["removed_offset_basis"] == "raw-response-utf8-byte.v1"
        assert raw.encode("utf-8")[offset : offset + 1] == b"}"
        assert raw.encode("utf-8")[offset + 1 :].strip() in {b"", b"```"}


def test_v1_journal_is_auditable_but_cannot_resume_as_v2(tmp_path: Path) -> None:
    current_identity = _identity(run_id="journal-v1-read-only")
    resume = begin_or_resume_pass1_call(run_dir=tmp_path, identity=current_identity)
    record_pass1_response(
        path=resume.path,
        identity=current_identity,
        raw_response="{}",
        provider_evidence={"usage_metadata": None},
    )
    legacy = json.loads(resume.path.read_text(encoding="utf-8"))
    legacy["processor_version"] = journal_module.LEGACY_PROCESSOR_VERSION
    legacy_body = {
        key: value for key, value in legacy.items() if key != "request_digest" and key != "state"
    }
    identity_keys = journal_module._IDENTITY_KEYS  # noqa: SLF001
    legacy_identity_body = {
        key: legacy[key] for key in identity_keys if key != "request_digest"
    }
    legacy["request_digest"] = journal_module._digest(legacy_identity_body)  # noqa: SLF001
    resume.path.write_text(json.dumps(legacy), encoding="utf-8")

    journal_module.validate_pass1_call_journal(legacy, journal_path=resume.path)
    assert legacy_body["processor_version"] == journal_module.LEGACY_PROCESSOR_VERSION
    legacy_identity = {key: legacy[key] for key in identity_keys}
    with pytest.raises(Pass1CallJournalError, match="read-only audit evidence"):
        begin_or_resume_pass1_call(run_dir=tmp_path, identity=legacy_identity)
    with pytest.raises(Pass1CallJournalError, match="read-only audit evidence"):
        record_pass1_response(
            path=resume.path,
            identity=legacy_identity,
            raw_response="{}",
            provider_evidence={"usage_metadata": None},
        )
    with pytest.raises(Pass1CallJournalError, match="identity mismatch"):
        begin_or_resume_pass1_call(run_dir=tmp_path, identity=current_identity)


def test_rejected_post_provider_candidate_is_retained_and_never_recalled(
    tmp_path: Path,
) -> None:
    run_id = "journal-rejected-candidate"
    payload = _payload(tmp_path, run_id)
    candidate = json.loads(_legacy_candidate())
    candidate["plan_units"][0].pop("source_refs")
    candidate["plan_units"][0]["source_ref_ids"] = ["span:sha256:" + "f" * 64]
    raw = json.dumps(candidate)
    chat = _InspectingChat(tmp_path / run_id, raw)

    with pytest.raises(pass1_act.Pass1AuthorityError):
        pass1_act.act(
            _state(payload),
            handle=_InspectingHandle(chat),
            model_id="gpt-test",
        )
    assert chat.calls == 1
    _path, received = _journal(tmp_path / run_id)
    assert received["state"] == "candidate_decoded"
    assert received["response_processing"]["parse_status"] == "decoded"
    assert received["raw_response"] == raw
    assert received["provider_evidence"]["response_id"] == "provider-response-1"

    with pytest.raises(pass1_act.Pass1AuthorityError):
        pass1_act.act(
            _state(payload),
            handle=SimpleNamespace(chat=_BombChat(), model_config_digest="sha256:" + "a" * 64),
            model_id="gpt-test",
        )


def test_unresolved_provider_exception_stays_ambiguous_and_forbids_recall(
    tmp_path: Path,
) -> None:
    run_id = "journal-provider-ambiguous"
    payload = _payload(tmp_path, run_id)

    class _RaisesAfterDispatch:
        def invoke(self, _messages: object) -> object:
            path, pre = _journal(tmp_path / run_id)
            assert pre["state"] == "call_in_progress"
            assert path.is_file()
            raise TimeoutError("provider outcome unknown")

    with pytest.raises(pass1_act.Pass1AuthorityError, match="outcome is ambiguous"):
        pass1_act.act(
            _state(payload),
            handle=SimpleNamespace(
                chat=_RaisesAfterDispatch(),
                model_config_digest="sha256:" + "b" * 64,
            ),
            model_id="gpt-test",
        )
    _path, ambiguous = _journal(tmp_path / run_id)
    assert ambiguous["state"] == "call_in_progress"
    assert ambiguous["dispatch_exception"] == {
        "type": "TimeoutError",
        "message": "provider outcome unknown",
    }

    with pytest.raises(pass1_act.Pass1AuthorityError, match="outcome is ambiguous"):
        pass1_act.act(
            _state(payload),
            handle=SimpleNamespace(chat=_BombChat(), model_config_digest="sha256:" + "b" * 64),
            model_id="gpt-test",
        )


def _identity(
    *,
    run_id: str,
    node_id: str = "04A",
    user: str = "user",
    catalog_digest: str = "sha256:" + "b" * 64,
) -> dict[str, Any]:
    return build_pass1_call_identity(
        run_id=run_id,
        node_id=node_id,
        model_id="gpt-test",
        model_config_digest="sha256:" + "a" * 64,
        catalog_digest=catalog_digest,
        messages=[
            {"role": "system", "content": "system"},
            {"role": "user", "content": user},
        ],
    )


def _completion(
    seed: str, *, run_dir: Path, run_id: str | None = None
) -> tuple[dict[str, str], dict[str, Any]]:
    effective_run_id = run_id or f"journal-transition-{seed}"
    catalog_digest = "sha256:" + "b" * 64
    span_id = "span:sha256:" + "d" * 64
    source_id = "slides/slide-1-source.md|sha256:" + "c" * 64
    plan = {
        "source_span_catalog_digest": catalog_digest,
        "plan_units": [
            {
                "unit_id": "u01",
                "title": seed,
                "scope_decision": "in-scope",
                "source_ref_ids": [span_id],
                "source_refs": ["anchor"],
                "cluster_id": "c-u01",
                "cluster_role": "head",
                "parent_slide_id": None,
            }
        ]
    }
    receipt_body = {
        "schema_version": "pass1-plan-authority.v2",
        "plan_digest": journal_module._digest(plan),  # noqa: SLF001
        "identities": [
            {
                "unit_id": "u01",
                "cluster_role": "head",
                "parent_slide_id": None,
                "source_refs": ["anchor"],
                "source_id": source_id,
                "active": True,
                "source_ref_ids": [span_id],
            }
        ],
        "catalog_digest": catalog_digest,
    }
    receipt = {
        **receipt_body,
        "authority_digest": journal_module._digest(receipt_body),  # noqa: SLF001
    }
    locked_scope = {"plan_units": plan["plan_units"], "locked": False}
    timestamp = "2026-07-14T12:00:00+00:00"
    base = {"run_id": effective_run_id, "gate": "G1A", "timestamp": timestamp}
    output = {
        "specialist_id": "irene_pass1",
        "model_id": "gpt-test",
        "lesson_plan": plan,
        "artifact_path": str(run_dir / "irene-pass1.md"),
        "locked_scope": locked_scope,
        "learning_events": [
            {**base, "event_type": "scope_decision.set", "payload": locked_scope},
            {
                **base,
                "event_type": "plan.locked",
                "payload": {"locked_scope": locked_scope},
            },
        ],
        "plan_authority_receipt": receipt,
        "plan_authority_receipt_path": str(
            run_dir / "irene-pass1.plan-authority.json"
        ),
        "usage": None,
    }
    prefix = json.dumps(output, sort_keys=True, separators=(",", ":"))
    return (
        {
            "plan_digest": receipt["plan_digest"],
            "authority_digest": receipt["authority_digest"],
            "output_digest": journal_module._digest(output),  # noqa: SLF001
        },
        {"cache_state": {"cache_prefix": prefix, "entries_count": 1}},
    )


def test_ambiguous_node_coordinate_rejects_request_drift_but_allows_other_node(
    tmp_path: Path,
) -> None:
    run_dir = tmp_path / "run"
    first = _identity(run_id="run")
    assert begin_or_resume_pass1_call(run_dir=run_dir, identity=first).state == "new"

    with pytest.raises(Pass1CallJournalError, match="identity mismatch"):
        begin_or_resume_pass1_call(
            run_dir=run_dir,
            identity=_identity(run_id="run", user="changed"),
        )

    other = begin_or_resume_pass1_call(
        run_dir=run_dir,
        identity=_identity(run_id="run", node_id="05"),
    )
    assert other.state == "new"


def test_completed_journal_rejects_different_result_bytes(tmp_path: Path) -> None:
    identity = _identity(run_id="run")
    resume = begin_or_resume_pass1_call(run_dir=tmp_path, identity=identity)
    record_pass1_response(
        path=resume.path,
        identity=identity,
        raw_response="{}",
        provider_evidence={"response_id": "response-1"},
    )
    first_identity, first_result = _completion(
        "one", run_dir=resume.path.parent, run_id="run"
    )
    complete_pass1_call(
        path=resume.path,
        identity=identity,
        result_identity=first_identity,
        result=first_result,
    )

    second_identity, second_result = _completion(
        "two", run_dir=resume.path.parent, run_id="run"
    )
    with pytest.raises(Pass1CallJournalError, match="cannot be replaced"):
        complete_pass1_call(
            path=resume.path,
            identity=identity,
            result_identity=second_identity,
            result=second_result,
        )


def test_dispatch_exception_evidence_scrubs_credentials(tmp_path: Path) -> None:
    identity = _identity(run_id="run")
    resume = begin_or_resume_pass1_call(run_dir=tmp_path, identity=identity)
    record_pass1_dispatch_exception(
        path=resume.path,
        identity=identity,
        exc=TimeoutError(
            "Bearer abcdefghijklmnop api_key=secret-value sk-abcdefghijk "
            "Authorization: Basic YWxhZGRpbjpvcGVuc2VzYW1l "
            "password=hunter2 client_secret=client-value access_token=access-value "
            "?X-Amz-Signature=signed-value&X-Amz-Credential=credential-value"
            "&X-Amz-Security-Token=session-value "
            "{\"access_token\":\"quoted-secret\"}"
        ),
    )

    retained = resume.path.read_text(encoding="utf-8")
    assert "abcdefghijklmnop" not in retained
    assert "secret-value" not in retained
    assert "sk-abcdefghijk" not in retained
    assert "YWxhZGRpbjpvcGVuc2VzYW1l" not in retained
    assert "hunter2" not in retained
    assert "client-value" not in retained
    assert "access-value" not in retained
    assert "signed-value" not in retained
    assert "quoted-secret" not in retained
    assert "credential-value" not in retained
    assert "session-value" not in retained
    assert retained.count("[REDACTED]") == 11


def test_completed_replay_advances_current_cache_count(tmp_path: Path) -> None:
    run_id = "journal-replay-current-count"
    payload = _payload(tmp_path, run_id)
    first = pass1_act.act(
        _state(payload),
        handle=_InspectingHandle(_InspectingChat(tmp_path / run_id, _legacy_candidate())),
        model_id="gpt-test",
    )
    replay = pass1_act.act(
        _state(payload, entries_count=7),
        handle=SimpleNamespace(chat=_BombChat(), model_config_digest="sha256:" + "a" * 64),
        model_id="gpt-test",
    )

    assert first["cache_state"]["entries_count"] == 1
    assert replay["cache_state"]["entries_count"] == 8
    assert replay["cache_state"]["cache_prefix"] == first["cache_state"]["cache_prefix"]


def test_completed_replay_mismatch_cannot_publish_over_current_artifacts(
    tmp_path: Path,
) -> None:
    run_id = "journal-replay-reject-before-publish"
    payload = _payload(tmp_path, run_id)
    first = pass1_act.act(
        _state(payload),
        handle=_InspectingHandle(_InspectingChat(tmp_path / run_id, _legacy_candidate())),
        model_id="gpt-test",
    )
    stored_output = json.loads(first["cache_state"]["cache_prefix"])
    artifact_path = Path(stored_output["artifact_path"])
    authority_path = Path(stored_output["plan_authority_receipt_path"])
    artifact_path.write_text("last committed plan\n", encoding="utf-8")
    authority_path.write_text("last committed authority\n", encoding="utf-8")

    journal_path, journal = _journal(tmp_path / run_id)
    journal["result_identity"]["plan_digest"] = "sha256:" + "f" * 64
    journal["result_identity_digest"] = journal_module._digest(  # noqa: SLF001
        journal["result_identity"]
    )
    journal_path.write_text(
        json.dumps(journal, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )

    with pytest.raises(pass1_act.Pass1AuthorityError, match="authority changed|unbound"):
        pass1_act.act(
            _state(payload),
            handle=SimpleNamespace(
                chat=_BombChat(), model_config_digest="sha256:" + "a" * 64
            ),
            model_id="gpt-test",
        )

    assert artifact_path.read_text(encoding="utf-8") == "last committed plan\n"
    assert authority_path.read_text(encoding="utf-8") == "last committed authority\n"


def test_completed_replay_rejects_rehashed_noncanonical_output_fields(
    tmp_path: Path,
) -> None:
    run_id = "journal-replay-full-output-reconstruction"
    payload = _payload(tmp_path, run_id)
    pass1_act.act(
        _state(payload),
        handle=_InspectingHandle(_InspectingChat(tmp_path / run_id, _legacy_candidate())),
        model_id="gpt-test",
    )
    journal_path, journal = _journal(tmp_path / run_id)
    output = json.loads(journal["result"]["cache_state"]["cache_prefix"])
    output["forged_graph_field"] = {"accepted": True}
    prefix = json.dumps(output, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
    journal["result"]["cache_state"]["cache_prefix"] = prefix
    journal["result_identity"]["output_digest"] = journal_module._digest(  # noqa: SLF001
        output
    )
    journal["result_identity_digest"] = journal_module._digest(  # noqa: SLF001
        journal["result_identity"]
    )
    journal["result_digest"] = journal_module._digest(journal["result"])  # noqa: SLF001
    journal_path.write_text(
        json.dumps(journal, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )

    with pytest.raises(
        pass1_act.Pass1AuthorityError, match="output disagrees|output shape"
    ):
        pass1_act.act(
            _state(payload),
            handle=SimpleNamespace(
                chat=_BombChat(), model_config_digest="sha256:" + "a" * 64
            ),
            model_id="gpt-test",
        )


def test_completed_replay_compares_json_types_not_python_numeric_equality(
    tmp_path: Path,
) -> None:
    run_id = "journal-replay-json-type-strict"
    payload = _payload(tmp_path, run_id)
    pass1_act.act(
        _state(payload),
        handle=_InspectingHandle(_InspectingChat(tmp_path / run_id, _legacy_candidate())),
        model_id="gpt-test",
    )
    journal_path, journal = _journal(tmp_path / run_id)
    output = json.loads(journal["result"]["cache_state"]["cache_prefix"])
    output["locked_scope"]["locked"] = 0
    output["learning_events"][0]["payload"]["locked"] = 0
    output["learning_events"][1]["payload"]["locked_scope"]["locked"] = 0
    prefix = json.dumps(output, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
    journal["result"]["cache_state"]["cache_prefix"] = prefix
    journal["result_identity"]["output_digest"] = journal_module._digest(  # noqa: SLF001
        output
    )
    journal["result_identity_digest"] = journal_module._digest(  # noqa: SLF001
        journal["result_identity"]
    )
    journal["result_digest"] = journal_module._digest(journal["result"])  # noqa: SLF001
    journal_path.write_text(
        json.dumps(journal, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )

    with pytest.raises(
        pass1_act.Pass1AuthorityError, match="output disagrees|output semantics"
    ):
        pass1_act.act(
            _state(payload),
            handle=SimpleNamespace(
                chat=_BombChat(), model_config_digest="sha256:" + "a" * 64
            ),
            model_id="gpt-test",
        )


def test_completed_replay_rejects_rehashed_result_identity_extension(
    tmp_path: Path,
) -> None:
    run_id = "journal-replay-result-identity-exact"
    payload = _payload(tmp_path, run_id)
    pass1_act.act(
        _state(payload),
        handle=_InspectingHandle(_InspectingChat(tmp_path / run_id, _legacy_candidate())),
        model_id="gpt-test",
    )
    journal_path, journal = _journal(tmp_path / run_id)
    journal["result_identity"]["forged_extension"] = {"accepted": True}
    journal["result_identity_digest"] = journal_module._digest(  # noqa: SLF001
        journal["result_identity"]
    )
    journal_path.write_text(
        json.dumps(journal, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )

    with pytest.raises(pass1_act.Pass1AuthorityError, match="identity"):
        pass1_act.act(
            _state(payload),
            handle=SimpleNamespace(
                chat=_BombChat(), model_config_digest="sha256:" + "a" * 64
            ),
            model_id="gpt-test",
        )


def test_completed_replay_rejects_rehashed_negative_provider_usage(
    tmp_path: Path,
) -> None:
    run_id = "journal-replay-provider-evidence-strict"
    payload = _payload(tmp_path, run_id)
    pass1_act.act(
        _state(payload),
        handle=_InspectingHandle(_InspectingChat(tmp_path / run_id, _legacy_candidate())),
        model_id="gpt-test",
    )
    journal_path, journal = _journal(tmp_path / run_id)
    journal["provider_evidence"]["usage_metadata"]["input_tokens"] = -999
    journal["provider_evidence_digest"] = journal_module._digest(  # noqa: SLF001
        journal["provider_evidence"]
    )
    output = json.loads(journal["result"]["cache_state"]["cache_prefix"])
    output["usage"]["input_tokens"] = -999
    prefix = json.dumps(output, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
    journal["result"]["cache_state"]["cache_prefix"] = prefix
    journal["result_identity"]["output_digest"] = journal_module._digest(  # noqa: SLF001
        output
    )
    journal["result_identity_digest"] = journal_module._digest(  # noqa: SLF001
        journal["result_identity"]
    )
    journal["result_digest"] = journal_module._digest(journal["result"])  # noqa: SLF001
    journal_path.write_text(
        json.dumps(journal, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )

    with pytest.raises(pass1_act.Pass1AuthorityError, match="provider evidence"):
        pass1_act.act(
            _state(payload),
            handle=SimpleNamespace(
                chat=_BombChat(), model_config_digest="sha256:" + "a" * 64
            ),
            model_id="gpt-test",
        )


def test_first_execution_rejects_invalid_provider_usage_before_completion(
    tmp_path: Path,
) -> None:
    run_id = "journal-first-run-provider-evidence-strict"
    payload = _payload(tmp_path, run_id)

    class _InvalidUsageChat(_InspectingChat):
        def invoke(self, messages: list[dict[str, str]]) -> SimpleNamespace:
            response = super().invoke(messages)
            response.usage_metadata = {
                "input_tokens": 10,
                "output_tokens": 5,
                "total_tokens": 99,
            }
            return response

    chat = _InvalidUsageChat(tmp_path / run_id, _legacy_candidate())
    with pytest.raises(pass1_act.Pass1AuthorityError, match="could not be normalized"):
        pass1_act.act(
            _state(payload),
            handle=_InspectingHandle(chat),
            model_id="gpt-test",
        )

    assert chat.calls == 1
    _path, retained = _journal(tmp_path / run_id)
    assert retained["state"] == "response_received"
    assert set(retained["provider_evidence"]) == {
        "response_type",
        "evidence_normalization_error",
    }


@pytest.mark.parametrize("state", ["call_in_progress", "response_received", "completed"])
def test_resume_rejects_unknown_top_level_fields_in_every_state(
    tmp_path: Path, state: str
) -> None:
    identity = _identity(run_id=f"journal-shape-{state}")
    resume = begin_or_resume_pass1_call(run_dir=tmp_path / state, identity=identity)
    if state in {"response_received", "completed"}:
        record_pass1_response(
            path=resume.path,
            identity=identity,
            raw_response="{}",
            provider_evidence={"usage_metadata": None},
        )
    if state == "completed":
        result_identity, result = _completion(
            state,
            run_dir=resume.path.parent,
            run_id=f"journal-shape-{state}",
        )
        complete_pass1_call(
            path=resume.path,
            identity=identity,
            result_identity=result_identity,
            result=result,
        )
    journal_path = resume.path
    journal = json.loads(journal_path.read_text(encoding="utf-8"))
    journal["forged_extension"] = {"accepted": True}
    journal_path.write_text(
        json.dumps(journal, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )

    with pytest.raises(Pass1CallJournalError, match="journal shape"):
        begin_or_resume_pass1_call(run_dir=tmp_path / state, identity=identity)


@pytest.mark.parametrize("transition", ["response", "exception", "complete"])
def test_state_transitions_cannot_launder_unknown_journal_fields(
    tmp_path: Path, transition: str
) -> None:
    identity = _identity(run_id=f"journal-transition-{transition}")
    resume = begin_or_resume_pass1_call(run_dir=tmp_path / transition, identity=identity)
    if transition == "complete":
        record_pass1_response(
            path=resume.path,
            identity=identity,
            raw_response="{}",
            provider_evidence={"usage_metadata": None},
        )
    journal = json.loads(resume.path.read_text(encoding="utf-8"))
    journal["forged_extension"] = {"accepted": True}
    resume.path.write_text(
        json.dumps(journal, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )

    with pytest.raises(Pass1CallJournalError, match="journal shape"):
        if transition == "response":
            record_pass1_response(
                path=resume.path,
                identity=identity,
                raw_response="{}",
                provider_evidence={"usage_metadata": None},
            )
        elif transition == "exception":
            record_pass1_dispatch_exception(
                path=resume.path, identity=identity, exc=TimeoutError("timeout")
            )
        else:
            result_identity, result = _completion(
                transition, run_dir=resume.path.parent
            )
            complete_pass1_call(
                path=resume.path,
                identity=identity,
                result_identity=result_identity,
                result=result,
            )


def test_empty_provider_exception_message_persists_canonical_fallback(
    tmp_path: Path,
) -> None:
    identity = _identity(run_id="journal-empty-exception")
    resume = begin_or_resume_pass1_call(run_dir=tmp_path, identity=identity)
    record_pass1_dispatch_exception(
        path=resume.path, identity=identity, exc=TimeoutError()
    )
    retained = json.loads(resume.path.read_text(encoding="utf-8"))
    assert retained["dispatch_exception"]["message"] == "(no message)"
    with pytest.raises(Pass1CallJournalError, match="ambiguous"):
        begin_or_resume_pass1_call(run_dir=tmp_path, identity=identity)


def test_durable_dispatch_exception_cannot_be_overwritten(tmp_path: Path) -> None:
    identity = _identity(run_id="journal-ambiguity-irreversible")
    resume = begin_or_resume_pass1_call(run_dir=tmp_path, identity=identity)
    record_pass1_dispatch_exception(
        path=resume.path, identity=identity, exc=TimeoutError("first timeout")
    )
    retained = resume.path.read_bytes()

    with pytest.raises(Pass1CallJournalError, match="already ambiguous"):
        record_pass1_response(
            path=resume.path,
            identity=identity,
            raw_response="{}",
            provider_evidence={"usage_metadata": None},
        )
    with pytest.raises(Pass1CallJournalError, match="already ambiguous"):
        record_pass1_dispatch_exception(
            path=resume.path, identity=identity, exc=TimeoutError("second timeout")
        )
    assert resume.path.read_bytes() == retained


@pytest.mark.parametrize(
    "provider_evidence",
    [
        {
            "response_type": "SimpleNamespace",
            "evidence_normalization_error": "ValueError",
        },
        {
            "response_type": "SimpleNamespace",
            "response_id": "response-1",
            "usage_metadata": None,
            "response_metadata": {},
            "unsupported_content_shape": "list",
        },
    ],
)
def test_terminal_error_evidence_cannot_be_marked_completed(
    tmp_path: Path, provider_evidence: dict[str, Any]
) -> None:
    identity = _identity(run_id=f"journal-terminal-{len(provider_evidence)}")
    resume = begin_or_resume_pass1_call(run_dir=tmp_path, identity=identity)
    record_pass1_response(
        path=resume.path,
        identity=identity,
        raw_response="{}",
        provider_evidence=provider_evidence,
    )
    result_identity, result = _completion(
        "terminal-error", run_dir=resume.path.parent, run_id=identity["run_id"]
    )
    with pytest.raises(Pass1CallJournalError, match="completed-result.*semantics"):
        complete_pass1_call(
            path=resume.path,
            identity=identity,
            result_identity=result_identity,
            result=result,
        )


def test_noncanonical_completed_result_shape_is_rejected(tmp_path: Path) -> None:
    identity = _identity(run_id="journal-completed-result-shape")
    resume = begin_or_resume_pass1_call(run_dir=tmp_path, identity=identity)
    record_pass1_response(
        path=resume.path,
        identity=identity,
        raw_response="{}",
        provider_evidence={"usage_metadata": None},
    )
    result_identity, _result = _completion(
        "bad-shape", run_dir=resume.path.parent
    )
    with pytest.raises(Pass1CallJournalError, match="completed output shape"):
        complete_pass1_call(
            path=resume.path,
            identity=identity,
            result_identity=result_identity,
            result={"cache_state": {"cache_prefix": "{}", "entries_count": 1}},
        )


@pytest.mark.parametrize(
    "field", ["plan_digest", "authority_digest", "output_digest"]
)
def test_completed_result_identity_must_be_derived_from_cached_output(
    tmp_path: Path, field: str
) -> None:
    run_id = f"journal-unbound-{field}"
    identity = _identity(run_id=run_id)
    resume = begin_or_resume_pass1_call(run_dir=tmp_path / field, identity=identity)
    record_pass1_response(
        path=resume.path,
        identity=identity,
        raw_response="{}",
        provider_evidence={"usage_metadata": None},
    )
    result_identity, result = _completion(
        field, run_dir=resume.path.parent, run_id=run_id
    )
    result_identity[field] = journal_module._digest("arbitrary")  # noqa: SLF001
    with pytest.raises(Pass1CallJournalError, match="identity is unbound"):
        complete_pass1_call(
            path=resume.path,
            identity=identity,
            result_identity=result_identity,
            result=result,
        )


def test_completed_authority_must_match_dispatched_catalog(tmp_path: Path) -> None:
    run_id = "journal-catalog-causal-binding"
    identity = _identity(
        run_id=run_id, catalog_digest="sha256:" + "e" * 64
    )
    resume = begin_or_resume_pass1_call(run_dir=tmp_path, identity=identity)
    record_pass1_response(
        path=resume.path,
        identity=identity,
        raw_response="{}",
        provider_evidence={"usage_metadata": None},
    )
    result_identity, result = _completion(
        "catalog-mismatch", run_dir=resume.path.parent, run_id=run_id
    )
    with pytest.raises(Pass1CallJournalError, match="identity is unbound"):
        complete_pass1_call(
            path=resume.path,
            identity=identity,
            result_identity=result_identity,
            result=result,
        )


def test_completed_artifact_paths_bind_actual_journal_directory(tmp_path: Path) -> None:
    run_id = "journal-path-causal-binding"
    identity = _identity(run_id=run_id)
    resume = begin_or_resume_pass1_call(run_dir=tmp_path / run_id, identity=identity)
    record_pass1_response(
        path=resume.path,
        identity=identity,
        raw_response="{}",
        provider_evidence={"usage_metadata": None},
    )
    result_identity, result = _completion(
        "wrong-root", run_dir=resume.path.parent, run_id=run_id
    )
    output = json.loads(result["cache_state"]["cache_prefix"])
    wrong_root = tmp_path / "other-root" / run_id
    output["artifact_path"] = str(wrong_root / "irene-pass1.md")
    output["plan_authority_receipt_path"] = str(
        wrong_root / "irene-pass1.plan-authority.json"
    )
    result["cache_state"]["cache_prefix"] = json.dumps(
        output, sort_keys=True, separators=(",", ":")
    )
    result_identity["output_digest"] = journal_module._digest(output)  # noqa: SLF001
    with pytest.raises(Pass1CallJournalError, match="output semantics"):
        complete_pass1_call(
            path=resume.path,
            identity=identity,
            result_identity=result_identity,
            result=result,
        )


def test_completed_planning_coverage_requires_strict_receipt(tmp_path: Path) -> None:
    run_id = "journal-planning-coverage-strict"
    identity = _identity(run_id=run_id)
    resume = begin_or_resume_pass1_call(run_dir=tmp_path / run_id, identity=identity)
    record_pass1_response(
        path=resume.path,
        identity=identity,
        raw_response="{}",
        provider_evidence={"usage_metadata": None},
    )
    result_identity, result = _completion(
        "bad-coverage", run_dir=resume.path.parent, run_id=run_id
    )
    output = json.loads(result["cache_state"]["cache_prefix"])
    provenance = {
        "schema_version": "0.1",
        "ratification_path": None,
        "ratification_digest": None,
        "ratified_los_path": None,
        "ratified_los_digest": None,
        "intent_path": None,
        "intent_digest": None,
        "coverage_lo_status": "framing_only",
    }
    output["lesson_plan"]["planning_provenance"] = provenance
    output["planning_provenance"] = provenance
    output["planning_context_coverage"] = {}
    receipt = output["plan_authority_receipt"]
    receipt["plan_digest"] = journal_module._digest(  # noqa: SLF001
        output["lesson_plan"]
    )
    receipt_body = {
        key: value for key, value in receipt.items() if key != "authority_digest"
    }
    receipt["authority_digest"] = journal_module._digest(receipt_body)  # noqa: SLF001
    result_identity["plan_digest"] = receipt["plan_digest"]
    result_identity["authority_digest"] = receipt["authority_digest"]
    result["cache_state"]["cache_prefix"] = json.dumps(
        output, sort_keys=True, separators=(",", ":")
    )
    result_identity["output_digest"] = journal_module._digest(output)  # noqa: SLF001
    with pytest.raises(Pass1CallJournalError, match="planning coverage"):
        complete_pass1_call(
            path=resume.path,
            identity=identity,
            result_identity=result_identity,
            result=result,
        )


def test_completed_planning_provenance_requires_projection_presence_parity(
    tmp_path: Path,
) -> None:
    run_id = "journal-planning-provenance-parity"
    identity = _identity(run_id=run_id)
    resume = begin_or_resume_pass1_call(run_dir=tmp_path / run_id, identity=identity)
    record_pass1_response(
        path=resume.path,
        identity=identity,
        raw_response="{}",
        provider_evidence={"usage_metadata": None},
    )
    result_identity, result = _completion(
        "missing-provenance", run_dir=resume.path.parent, run_id=run_id
    )
    output = json.loads(result["cache_state"]["cache_prefix"])
    provenance = {
        "schema_version": "0.1",
        "ratification_path": None,
        "ratification_digest": None,
        "ratified_los_path": None,
        "ratified_los_digest": None,
        "intent_path": None,
        "intent_digest": None,
        "coverage_lo_status": "framing_only",
    }
    output["lesson_plan"]["planning_provenance"] = provenance
    receipt = output["plan_authority_receipt"]
    receipt["plan_digest"] = journal_module._digest(  # noqa: SLF001
        output["lesson_plan"]
    )
    receipt_body = {
        key: value for key, value in receipt.items() if key != "authority_digest"
    }
    receipt["authority_digest"] = journal_module._digest(receipt_body)  # noqa: SLF001
    result_identity["plan_digest"] = receipt["plan_digest"]
    result_identity["authority_digest"] = receipt["authority_digest"]
    result_identity["output_digest"] = journal_module._digest(output)  # noqa: SLF001
    result["cache_state"]["cache_prefix"] = json.dumps(
        output, sort_keys=True, separators=(",", ":")
    )
    with pytest.raises(Pass1CallJournalError, match="projections are split"):
        complete_pass1_call(
            path=resume.path,
            identity=identity,
            result_identity=result_identity,
            result=result,
        )


@pytest.mark.parametrize("projection", ["null-plan", "provenance-without-coverage"])
def test_completed_planning_projections_must_cooccur_and_reject_null(
    tmp_path: Path, projection: str
) -> None:
    run_id = f"journal-planning-{projection}"
    identity = _identity(run_id=run_id)
    resume = begin_or_resume_pass1_call(run_dir=tmp_path / run_id, identity=identity)
    record_pass1_response(
        path=resume.path,
        identity=identity,
        raw_response="{}",
        provider_evidence={"usage_metadata": None},
    )
    result_identity, result = _completion(
        projection, run_dir=resume.path.parent, run_id=run_id
    )
    output = json.loads(result["cache_state"]["cache_prefix"])
    provenance = {
        "schema_version": "0.1",
        "ratification_path": None,
        "ratification_digest": None,
        "ratified_los_path": None,
        "ratified_los_digest": None,
        "intent_path": None,
        "intent_digest": None,
        "coverage_lo_status": "framing_only",
    }
    output["lesson_plan"]["planning_provenance"] = (
        None if projection == "null-plan" else provenance
    )
    if projection == "provenance-without-coverage":
        output["planning_provenance"] = provenance
    receipt = output["plan_authority_receipt"]
    receipt["plan_digest"] = journal_module._digest(  # noqa: SLF001
        output["lesson_plan"]
    )
    receipt_body = {
        key: value for key, value in receipt.items() if key != "authority_digest"
    }
    receipt["authority_digest"] = journal_module._digest(receipt_body)  # noqa: SLF001
    result_identity["plan_digest"] = receipt["plan_digest"]
    result_identity["authority_digest"] = receipt["authority_digest"]
    result_identity["output_digest"] = journal_module._digest(output)  # noqa: SLF001
    result["cache_state"]["cache_prefix"] = json.dumps(
        output, sort_keys=True, separators=(",", ":")
    )
    with pytest.raises(Pass1CallJournalError, match="projections are split"):
        complete_pass1_call(
            path=resume.path,
            identity=identity,
            result_identity=result_identity,
            result=result,
        )


@pytest.mark.parametrize(
    ("case", "coverage_status", "ratification_path", "ratification_digest", "accept"),
    [
        ("framing-contradiction", "absent", None, None, False),
        ("path-with-null-digest", "present", "planning-ratification.json", None, True),
        (
            "digest-without-path",
            "present",
            None,
            "sha256:" + "f" * 64,
            False,
        ),
    ],
)
def test_completed_planning_status_and_path_digest_direction(
    tmp_path: Path,
    case: str,
    coverage_status: str,
    ratification_path: str | None,
    ratification_digest: str | None,
    accept: bool,
) -> None:
    run_id = f"journal-planning-{case}"
    identity = _identity(run_id=run_id)
    resume = begin_or_resume_pass1_call(run_dir=tmp_path / run_id, identity=identity)
    record_pass1_response(
        path=resume.path,
        identity=identity,
        raw_response="{}",
        provider_evidence={"usage_metadata": None},
    )
    result_identity, result = _completion(
        case, run_dir=resume.path.parent, run_id=run_id
    )
    output = json.loads(result["cache_state"]["cache_prefix"])
    coverage = {
        "schema_version": "0.1",
        "context_present": True,
        "lo_coverage": coverage_status,
        "supported_objective_ids": [],
        "weak_or_missing_objective_ids": (
            ["lo-1"] if coverage_status == "absent" else []
        ),
        "purpose_acknowledged": False,
        "audience_acknowledged": False,
        "notes": "",
    }
    provenance = {
        "schema_version": "0.1",
        "ratification_path": ratification_path,
        "ratification_digest": ratification_digest,
        "ratified_los_path": None,
        "ratified_los_digest": None,
        "intent_path": None,
        "intent_digest": None,
        "coverage_lo_status": "framing_only",
    }
    output["lesson_plan"]["planning_provenance"] = provenance
    output["planning_provenance"] = provenance
    output["planning_context_coverage"] = coverage
    receipt = output["plan_authority_receipt"]
    receipt["plan_digest"] = journal_module._digest(  # noqa: SLF001
        output["lesson_plan"]
    )
    receipt_body = {
        key: value for key, value in receipt.items() if key != "authority_digest"
    }
    receipt["authority_digest"] = journal_module._digest(receipt_body)  # noqa: SLF001
    result_identity["plan_digest"] = receipt["plan_digest"]
    result_identity["authority_digest"] = receipt["authority_digest"]
    result_identity["output_digest"] = journal_module._digest(output)  # noqa: SLF001
    result["cache_state"]["cache_prefix"] = json.dumps(
        output, sort_keys=True, separators=(",", ":")
    )

    if accept:
        complete_pass1_call(
            path=resume.path,
            identity=identity,
            result_identity=result_identity,
            result=result,
        )
        assert begin_or_resume_pass1_call(
            run_dir=resume.path.parent, identity=identity
        ).state == "completed"
    else:
        with pytest.raises(Pass1CallJournalError, match="planning provenance"):
            complete_pass1_call(
                path=resume.path,
                identity=identity,
                result_identity=result_identity,
                result=result,
            )


@pytest.mark.parametrize(
    "coverage_update",
    [
        {"context_present": False},
        {"lo_coverage": "present", "weak_or_missing_objective_ids": ["lo-1"]},
        {"lo_coverage": "partial", "weak_or_missing_objective_ids": []},
        {
            "lo_coverage": "absent",
            "supported_objective_ids": ["lo-1"],
            "weak_or_missing_objective_ids": ["lo-2"],
        },
        {
            "lo_coverage": "absent",
            "supported_objective_ids": [],
            "weak_or_missing_objective_ids": [],
        },
    ],
)
def test_completed_planning_coverage_rejects_states_irene_cannot_emit(
    tmp_path: Path,
    coverage_update: dict[str, Any],
) -> None:
    run_id = "journal-impossible-planning-coverage"
    identity = _identity(run_id=run_id)
    resume = begin_or_resume_pass1_call(run_dir=tmp_path / run_id, identity=identity)
    record_pass1_response(
        path=resume.path,
        identity=identity,
        raw_response="{}",
        provider_evidence={"usage_metadata": None},
    )
    result_identity, result = _completion(
        "impossible-planning-coverage", run_dir=resume.path.parent, run_id=run_id
    )
    output = json.loads(result["cache_state"]["cache_prefix"])
    coverage = {
        "schema_version": "0.1",
        "context_present": True,
        "lo_coverage": "present",
        "supported_objective_ids": [],
        "weak_or_missing_objective_ids": [],
        "purpose_acknowledged": False,
        "audience_acknowledged": False,
        "notes": "",
        **coverage_update,
    }
    provenance = {
        "schema_version": "0.1",
        "ratification_path": None,
        "ratification_digest": None,
        "ratified_los_path": None,
        "ratified_los_digest": None,
        "intent_path": None,
        "intent_digest": None,
        "coverage_lo_status": coverage["lo_coverage"],
    }
    output["lesson_plan"]["planning_provenance"] = provenance
    output["planning_provenance"] = provenance
    output["planning_context_coverage"] = coverage
    receipt = output["plan_authority_receipt"]
    receipt["plan_digest"] = journal_module._digest(output["lesson_plan"])  # noqa: SLF001
    receipt_body = {
        key: value for key, value in receipt.items() if key != "authority_digest"
    }
    receipt["authority_digest"] = journal_module._digest(receipt_body)  # noqa: SLF001
    result_identity["plan_digest"] = receipt["plan_digest"]
    result_identity["authority_digest"] = receipt["authority_digest"]
    result_identity["output_digest"] = journal_module._digest(output)  # noqa: SLF001
    result["cache_state"]["cache_prefix"] = json.dumps(
        output, sort_keys=True, separators=(",", ":")
    )

    with pytest.raises(Pass1CallJournalError, match="planning coverage"):
        complete_pass1_call(
            path=resume.path,
            identity=identity,
            result_identity=result_identity,
            result=result,
        )


def test_provider_text_accepts_supported_structured_text_blocks() -> None:
    assert pass1_act._provider_text(
        [
            {"type": "text", "text": '{"plan_units":'},
            {"type": "output_text", "text": "[]}"},
        ]
    ) == '{"plan_units":[]}'

    with pytest.raises(pass1_act.Pass1AuthorityError, match="unsupported content blocks"):
        pass1_act._provider_text([{"type": "image", "url": "secret"}])


def test_prompt_context_guard_refuses_before_dispatch() -> None:
    handle = SimpleNamespace(chat=SimpleNamespace(max_completion_tokens=399_999))
    with pytest.raises(pass1_act.Pass1AuthorityError, match="context budget"):
        pass1_act._assert_prompt_fits_context(
            handle=handle,
            model_id="gpt-5.4",
            system_msg="system",
            user_msg="user",
        )


def test_unsupported_returned_content_is_durable_and_not_recalled(tmp_path: Path) -> None:
    run_id = "unsupported-returned-content"
    payload = _payload(tmp_path, run_id)

    class _UnsupportedChat:
        calls = 0

        def invoke(self, _messages: object) -> SimpleNamespace:
            self.calls += 1
            return SimpleNamespace(
                content=[{"type": "image", "url": "not-retained"}],
                usage_metadata={"input_tokens": 10, "output_tokens": 2},
                id="response-unsupported",
            )

    chat = _UnsupportedChat()
    handle = SimpleNamespace(chat=chat, model_config_digest="sha256:" + "a" * 64)
    with pytest.raises(pass1_act.Pass1AuthorityError, match="unsupported content"):
        pass1_act.act(_state(payload), handle=handle, model_id="gpt-test")
    _path, retained = _journal(tmp_path / run_id)
    assert retained["state"] == "response_received"
    assert retained["provider_evidence"]["unsupported_content_shape"] == "list"
    assert "not-retained" not in json.dumps(retained)

    with pytest.raises(pass1_act.Pass1AuthorityError, match="unsupported content"):
        pass1_act.act(
            _state(payload),
            handle=SimpleNamespace(
                chat=_BombChat(), model_config_digest="sha256:" + "a" * 64
            ),
            model_id="gpt-test",
        )
    assert chat.calls == 1
