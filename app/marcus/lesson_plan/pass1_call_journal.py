"""Crash-safe provider-call evidence for Irene Pass-1.

The journal is committed before dispatch and again immediately after a provider
response returns.  A pre-dispatch record without a response is intentionally
ambiguous and can never authorize an automatic recall.  A returned response is
safe to replay only through deterministic Pass-1 validation and projection.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import stat
import tempfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Literal

SCHEMA_VERSION = "irene-pass1-call.v1"
LEGACY_PROCESSOR_VERSION = "irene-pass1-response-processor.v1"
PROCESSOR_VERSION = "irene-pass1-response-processor.v2"
SUPPORTED_PROCESSOR_VERSIONS = frozenset({LEGACY_PROCESSOR_VERSION, PROCESSOR_VERSION})
_DIGEST_PREFIX = "sha256:"
_IDENTITY_KEYS = frozenset(
    {
        "schema_version",
        "processor_version",
        "request_digest",
        "run_id",
        "node_id",
        "model_id",
        "model_config_digest",
        "catalog_digest",
        "messages",
        "messages_digest",
    }
)
_PROVIDER_EVIDENCE_KEYS = frozenset(
    {"response_type", "response_id", "usage_metadata", "response_metadata"}
)
_RESPONSE_METADATA_KEYS = frozenset(
    {"model_name", "model", "finish_reason", "system_fingerprint", "service_tier"}
)
_USAGE_METADATA_KEYS = frozenset(
    {
        "input_tokens",
        "output_tokens",
        "total_tokens",
        "input_token_details",
        "output_token_details",
    }
)
_RESULT_IDENTITY_KEYS = frozenset(
    {"plan_digest", "authority_digest", "output_digest"}
)
_PROCESSING_KEYS = frozenset(
    {
        "schema_version",
        "journal_processor_version",
        "executed_processor_version",
        "raw_response_digest",
        "action",
        "framing",
        "removed_byte",
        "removed_offset",
        "removed_offset_basis",
        "processed_candidate_digest",
        "parse_status",
        "digest_recipe",
    }
)


class Pass1CallJournalError(ValueError):
    """The Irene call journal is unsafe, corrupt, or identity-inconsistent."""


class Pass1CallAmbiguousError(Pass1CallJournalError):
    """A dispatch was committed but no durable provider response is known."""


@dataclass(frozen=True)
class Pass1CallResume:
    path: Path
    state: Literal["new", "response_received", "candidate_decoded", "completed"]
    raw_response: str | None = None
    provider_evidence: dict[str, Any] | None = None
    result: dict[str, Any] | None = None
    result_identity: dict[str, Any] | None = None
    response_processing: dict[str, Any] | None = None


def _canonical_bytes(value: object) -> bytes:
    try:
        return json.dumps(
            value,
            sort_keys=True,
            ensure_ascii=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise Pass1CallJournalError("Irene call journal is not canonical JSON") from exc


def _digest(value: object) -> str:
    return _DIGEST_PREFIX + hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _is_digest(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 71
        and value.startswith(_DIGEST_PREFIX)
        and all(character in "0123456789abcdef" for character in value[7:])
    )


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise Pass1CallJournalError(f"duplicate journal key {key!r}")
        result[key] = value
    return result


def _json_safe(value: object) -> object:
    if value is None or isinstance(value, (str, int, bool)):
        return value
    if isinstance(value, float):
        if value != value or value in {float("inf"), float("-inf")}:
            return str(value)
        return value
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    if hasattr(value, "model_dump"):
        return _json_safe(value.model_dump(mode="json"))
    return str(value)


def response_provider_evidence(response: object) -> dict[str, Any]:
    """Capture an allowlisted, secret-free provider receipt."""
    raw_metadata = _json_safe(getattr(response, "response_metadata", None))
    metadata = raw_metadata if isinstance(raw_metadata, dict) else {}
    allowed_metadata = {
        key: metadata[key]
        for key in (
            "model_name",
            "model",
            "finish_reason",
            "system_fingerprint",
            "service_tier",
        )
        if key in metadata
    }
    evidence: dict[str, Any] = {
        "response_type": type(response).__name__,
        "response_id": _json_safe(getattr(response, "id", None)),
        "usage_metadata": _json_safe(getattr(response, "usage_metadata", None)),
        "response_metadata": allowed_metadata,
    }
    normalized = json.loads(_canonical_bytes(_scrub_json_secrets(evidence)))
    validate_provider_evidence(normalized)
    return normalized


def _validate_usage_metadata(value: object) -> None:
    if value is None:
        return
    if not isinstance(value, dict) or not set(value).issubset(_USAGE_METADATA_KEYS):
        raise Pass1CallJournalError("Irene provider evidence usage metadata is invalid")
    for key in ("input_tokens", "output_tokens", "total_tokens"):
        token_count = value.get(key)
        if key in value and (type(token_count) is not int or token_count < 0):
            raise Pass1CallJournalError("Irene provider evidence token usage is invalid")
    for key in ("input_token_details", "output_token_details"):
        if key not in value:
            continue
        details = value[key]
        if not isinstance(details, dict) or any(
            not isinstance(name, str)
            or not name
            or type(count) is not int
            or count < 0
            for name, count in details.items()
        ):
            raise Pass1CallJournalError("Irene provider evidence token details are invalid")
    if all(key in value for key in ("input_tokens", "output_tokens", "total_tokens")) and (
        value["total_tokens"] != value["input_tokens"] + value["output_tokens"]
    ):
        raise Pass1CallJournalError("Irene provider evidence total token usage is invalid")


def validate_provider_evidence(value: dict[str, Any]) -> None:
    """Fail closed unless provider evidence has the canonical safe shape."""
    keys = set(value)
    if keys == {"response_type", "evidence_normalization_error"}:
        if not all(isinstance(value[key], str) and value[key] for key in keys):
            raise Pass1CallJournalError("Irene provider evidence error posture is invalid")
        return
    expected_keys = set(_PROVIDER_EVIDENCE_KEYS)
    if "unsupported_content_shape" in keys:
        expected_keys.add("unsupported_content_shape")
    if keys != expected_keys:
        raise Pass1CallJournalError("Irene provider evidence shape is invalid")
    if not isinstance(value["response_type"], str) or not value["response_type"]:
        raise Pass1CallJournalError("Irene provider evidence response type is invalid")
    if value["response_id"] is not None and (
        not isinstance(value["response_id"], str) or not value["response_id"]
    ):
        raise Pass1CallJournalError("Irene provider evidence response ID is invalid")
    metadata = value["response_metadata"]
    if (
        not isinstance(metadata, dict)
        or not set(metadata).issubset(_RESPONSE_METADATA_KEYS)
        or any(item is not None and not isinstance(item, str) for item in metadata.values())
    ):
        raise Pass1CallJournalError("Irene provider response metadata is invalid")
    if "unsupported_content_shape" in value and (
        not isinstance(value["unsupported_content_shape"], str)
        or not value["unsupported_content_shape"]
    ):
        raise Pass1CallJournalError("Irene provider evidence content shape is invalid")
    _validate_usage_metadata(value["usage_metadata"])


def _canonical_provider_evidence(value: dict[str, Any]) -> dict[str, Any]:
    safe = json.loads(_canonical_bytes(_json_safe(value)))
    if set(safe) != {"response_type", "evidence_normalization_error"}:
        unknown = set(safe) - set(_PROVIDER_EVIDENCE_KEYS) - {"unsupported_content_shape"}
        if unknown:
            raise Pass1CallJournalError("Irene provider evidence shape is invalid")
        safe = {
            "response_type": safe.get("response_type", "unknown"),
            "response_id": safe.get("response_id"),
            "usage_metadata": safe.get("usage_metadata"),
            "response_metadata": safe.get("response_metadata", {}),
            **(
                {"unsupported_content_shape": safe["unsupported_content_shape"]}
                if "unsupported_content_shape" in safe
                else {}
            ),
        }
    validate_provider_evidence(safe)
    return safe


_SECRET_PATTERNS = (
    re.compile(r"\bsk-[A-Za-z0-9_-]{8,}\b"),
    re.compile(r"(?i)\b(bearer\s+)[A-Za-z0-9._~+/=-]{8,}"),
    re.compile(r"(?i)\b(basic\s+)[A-Za-z0-9+/=]{8,}"),
    re.compile(r"(?i)\b(api[_-]?key\s*[=:]\s*)[^\s,;]+"),
    re.compile(
        r"(?i)\b((?:password|client[_-]?secret|access[_-]?token|refresh[_-]?token|"
        r"security[_-]?token|credential|access[_-]?key|signature|sig|"
        r"x-amz-(?:signature|credential|security-token))\s*[=:]\s*)[^\s,;&]+"
    ),
    re.compile(
        r'(?i)(["\'](?:password|client[_-]?secret|access[_-]?token|refresh[_-]?token|'
        r'api[_-]?key)["\']\s*:\s*["\'])[^"\']+(["\'])'
    ),
)

_SECRET_KEY_FRAGMENTS = (
    "password",
    "api_key",
    "apikey",
    "client_secret",
    "access_token",
    "refresh_token",
    "security_token",
    "credential",
    "access_key",
    "authorization",
    "signature",
)


def _scrub_secrets(value: str) -> str:
    scrubbed = value
    for pattern in _SECRET_PATTERNS:
        scrubbed = pattern.sub(
            lambda match: (match.group(1) if match.lastindex else "") + "[REDACTED]", scrubbed
        )
    return scrubbed


def _scrub_json_secrets(value: object) -> object:
    if isinstance(value, str):
        return _scrub_secrets(value)
    if isinstance(value, dict):
        return {
            str(key): (
                "[REDACTED]"
                if any(fragment in str(key).lower() for fragment in _SECRET_KEY_FRAGMENTS)
                else _scrub_json_secrets(item)
            )
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [_scrub_json_secrets(item) for item in value]
    return value


def build_pass1_call_identity(
    *,
    run_id: str,
    node_id: str,
    model_id: str,
    model_config_digest: str,
    catalog_digest: str,
    messages: list[dict[str, str]],
) -> dict[str, Any]:
    if (
        not run_id
        or re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}", node_id) is None
        or not model_id
        or not _is_digest(catalog_digest)
    ):
        raise Pass1CallJournalError("Irene call identity is invalid")
    if not _is_digest(model_config_digest):
        raise Pass1CallJournalError("Irene model-config digest is invalid")
    if (
        len(messages) != 2
        or [message.get("role") for message in messages] != ["system", "user"]
        or not all(
            set(message) == {"role", "content"}
            and isinstance(message.get("content"), str)
            for message in messages
        )
    ):
        raise Pass1CallJournalError("Irene call messages are invalid")
    canonical_messages = json.loads(_canonical_bytes(messages))
    body: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "processor_version": PROCESSOR_VERSION,
        "run_id": run_id,
        "node_id": node_id,
        "model_id": model_id,
        "model_config_digest": model_config_digest,
        "catalog_digest": catalog_digest,
        "messages": canonical_messages,
        "messages_digest": _digest(canonical_messages),
    }
    return {**body, "request_digest": _digest(body)}


def _fsync_directory(path: Path) -> None:
    if os.name == "nt":
        import ctypes

        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        handle = kernel32.CreateFileW(
            str(path),
            0x40000000,
            0x00000007,
            None,
            3,
            0x02000000,
            None,
        )
        if handle == -1:
            raise OSError(ctypes.get_last_error(), "cannot open journal directory")
        try:
            if not kernel32.FlushFileBuffers(handle):
                raise OSError(ctypes.get_last_error(), "cannot flush journal directory")
        finally:
            kernel32.CloseHandle(handle)
        return
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _atomic_json(path: Path, payload: dict[str, Any]) -> None:
    if path.is_symlink() or (path.exists() and not path.is_file()):
        raise Pass1CallJournalError("Irene call journal coordinate is unsafe")
    serialized = _canonical_bytes(payload) + b"\n"
    descriptor, temporary_name = tempfile.mkstemp(
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(serialized)
            stream.flush()
            os.fsync(stream.fileno())
        if path.is_symlink() or (path.exists() and not path.is_file()):
            raise Pass1CallJournalError("Irene call journal coordinate is unsafe")
        os.replace(temporary, path)
        _fsync_directory(path.parent)
    finally:
        temporary.unlink(missing_ok=True)


def _load(path: Path) -> dict[str, Any]:
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        path_before = path.lstat()
        if not stat.S_ISREG(path_before.st_mode):
            raise Pass1CallJournalError("Irene call journal is not a regular file")
        descriptor = os.open(path, flags)
        try:
            before = os.fstat(descriptor)
            if not stat.S_ISREG(before.st_mode):
                raise Pass1CallJournalError("Irene call journal is not a regular file")
            if (path_before.st_dev, path_before.st_ino) != (before.st_dev, before.st_ino):
                raise Pass1CallJournalError("Irene call journal changed before read")
            with os.fdopen(descriptor, "rb", closefd=False) as stream:
                raw = stream.read()
            after = os.fstat(descriptor)
            path_after = path.lstat()
            stable_fields = ("st_dev", "st_ino", "st_size", "st_mtime_ns")
            if any(
                getattr(before, field) != getattr(after, field) for field in stable_fields
            ) or any(
                getattr(after, field) != getattr(path_after, field) for field in stable_fields
            ):
                raise Pass1CallJournalError("Irene call journal changed during read")
        finally:
            os.close(descriptor)
        payload = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_object)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise Pass1CallJournalError(f"Irene call journal is unreadable: {exc}") from exc
    if not isinstance(payload, dict):
        raise Pass1CallJournalError("Irene call journal root is invalid")
    return payload


def _validate_identity(identity: dict[str, Any]) -> None:
    if set(identity) != _IDENTITY_KEYS:
        raise Pass1CallJournalError("Irene call identity shape is invalid")
    if (
        identity.get("schema_version") != SCHEMA_VERSION
        or identity.get("processor_version") not in SUPPORTED_PROCESSOR_VERSIONS
        or not isinstance(identity.get("run_id"), str)
        or not identity["run_id"]
        or not isinstance(identity.get("node_id"), str)
        or re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}", identity["node_id"])
        is None
        or not isinstance(identity.get("model_id"), str)
        or not identity["model_id"]
        or not _is_digest(identity.get("model_config_digest"))
        or not _is_digest(identity.get("catalog_digest"))
    ):
        raise Pass1CallJournalError("Irene call identity semantics are invalid")
    messages = identity.get("messages")
    if (
        not isinstance(messages, list)
        or len(messages) != 2
        or [message.get("role") if isinstance(message, dict) else None for message in messages]
        != ["system", "user"]
        or any(
            not isinstance(message, dict)
            or set(message) != {"role", "content"}
            or not isinstance(message["content"], str)
            for message in messages
        )
    ):
        raise Pass1CallJournalError("Irene call messages are invalid")
    body = {key: identity[key] for key in identity if key != "request_digest"}
    if identity.get("request_digest") != _digest(body):
        raise Pass1CallJournalError("Irene call request digest mismatch")
    if identity.get("messages_digest") != _digest(identity.get("messages")):
        raise Pass1CallJournalError("Irene call messages digest mismatch")


def _assert_same_identity(journal: dict[str, Any], identity: dict[str, Any]) -> None:
    if any(journal.get(key) != identity[key] for key in _IDENTITY_KEYS):
        raise Pass1CallJournalError("Irene call journal identity mismatch")


def _require_current_processor(identity: dict[str, Any]) -> None:
    if identity.get("processor_version") != PROCESSOR_VERSION:
        raise Pass1CallJournalError(
            "legacy Irene call journals are read-only audit evidence"
        )


def _reject_json_constant(value: str) -> None:
    raise Pass1CallJournalError(f"non-standard JSON constant {value!r}")


def _response_frame(raw_response: str) -> tuple[str, str, int]:
    json_ws = " \t\r\n"
    leading = len(raw_response) - len(raw_response.lstrip(json_ws))
    outer = raw_response.strip(json_ws)
    candidate = outer
    framing = "plain"
    candidate_start = leading
    if outer.startswith("```json") or outer.endswith("```"):
        prefix = "```json\r\n" if outer.startswith("```json\r\n") else "```json\n"
        suffix = "\r\n```" if outer.endswith("\r\n```") else "\n```"
        if not outer.startswith(prefix) or not outer.endswith(suffix):
            raise Pass1CallJournalError("Irene response-processing framing is invalid")
        candidate = outer[len(prefix) : -len(suffix)]
        framing = "json-code-fence"
        candidate_start = leading + len(prefix)
    return candidate, framing, candidate_start


def _expected_processing_from_raw(raw_response: str) -> dict[str, Any]:
    candidate, framing, candidate_start = _response_frame(raw_response)
    action = "strict-json"
    removed_byte: str | None = None
    removed_offset: int | None = None
    try:
        decoded = json.loads(
            candidate,
            object_pairs_hook=_unique_object,
            parse_constant=_reject_json_constant,
        )
    except Pass1CallJournalError as exc:
        raise Pass1CallJournalError(
            "Irene response-processing candidate is invalid"
        ) from exc
    except json.JSONDecodeError as exc:
        if exc.msg != "Extra data":
            raise Pass1CallJournalError(
                "Irene response-processing candidate is invalid"
            ) from exc
        removed_index = len(candidate.rstrip(" \t\r\n")) - 1
        if removed_index < 0 or candidate[removed_index] != "}":
            raise Pass1CallJournalError(
                "Irene response-processing candidate is invalid"
            ) from exc
        repaired = candidate[:removed_index] + candidate[removed_index + 1 :]
        try:
            decoded = json.loads(
                repaired,
                object_pairs_hook=_unique_object,
                parse_constant=_reject_json_constant,
            )
        except (json.JSONDecodeError, Pass1CallJournalError) as raw_exc:
            raise Pass1CallJournalError(
                "Irene response-processing candidate is invalid"
            ) from raw_exc
        action = "drop-one-surplus-final-rbrace"
        removed_byte = "}"
        removed_offset = len(
            raw_response[: candidate_start + removed_index].encode("utf-8")
        )
    if not isinstance(decoded, dict):
        raise Pass1CallJournalError("Irene response-processing candidate is invalid")
    return {
        "action": action,
        "framing": framing,
        "removed_byte": removed_byte,
        "removed_offset": removed_offset,
        "removed_offset_basis": (
            "raw-response-utf8-byte.v1" if removed_offset is not None else None
        ),
        "processed_candidate_digest": _digest(decoded),
    }


def _validate_journal_shape(journal: dict[str, Any], state: object) -> None:
    base = set(_IDENTITY_KEYS) | {"state"}
    processing = {"response_processing", "response_processing_digest"}
    is_v2 = journal.get("processor_version") == PROCESSOR_VERSION
    if state == "call_in_progress":
        expected = base
        if "dispatch_exception" in journal or "dispatch_exception_digest" in journal:
            expected |= {"dispatch_exception", "dispatch_exception_digest"}
            evidence = journal.get("dispatch_exception")
            if (
                not isinstance(evidence, dict)
                or set(evidence) != {"type", "message"}
                or not all(isinstance(item, str) and item for item in evidence.values())
                or journal.get("dispatch_exception_digest") != _digest(evidence)
            ):
                raise Pass1CallJournalError("Irene dispatch-exception evidence is invalid")
    elif state == "response_received":
        expected = base | {
            "raw_response",
            "raw_response_digest",
            "provider_evidence",
            "provider_evidence_digest",
        }
    elif state == "candidate_decoded" and is_v2:
        expected = base | {
            "raw_response",
            "raw_response_digest",
            "provider_evidence",
            "provider_evidence_digest",
        } | processing
    elif state == "completed":
        expected = base | {
            "raw_response",
            "raw_response_digest",
            "provider_evidence",
            "provider_evidence_digest",
            "result_identity",
            "result_identity_digest",
            "result",
            "result_digest",
        }
        if is_v2:
            expected |= processing
    else:
        raise Pass1CallJournalError("Irene call journal state is invalid")
    if set(journal) != expected:
        raise Pass1CallJournalError("Irene call journal shape is invalid")


def validate_pass1_call_journal(
    journal: dict[str, Any], *, journal_path: Path
) -> None:
    """Validate one complete journal envelope independently of its consumer."""
    if not isinstance(journal, dict):
        raise Pass1CallJournalError("Irene call journal root is invalid")
    identity = {key: journal.get(key) for key in _IDENTITY_KEYS}
    _validate_identity(identity)
    state = journal.get("state")
    _validate_journal_shape(journal, state)
    if state in {"response_received", "candidate_decoded", "completed"}:
        raw_response = journal.get("raw_response")
        provider_evidence = journal.get("provider_evidence")
        if (
            not isinstance(raw_response, str)
            or journal.get("raw_response_digest") != _digest(raw_response)
            or not isinstance(provider_evidence, dict)
            or journal.get("provider_evidence_digest") != _digest(provider_evidence)
        ):
            raise Pass1CallJournalError("Irene returned-response evidence is invalid")
        validate_provider_evidence(provider_evidence)
    if state in {"candidate_decoded", "completed"} and journal.get(
        "processor_version"
    ) == PROCESSOR_VERSION:
        processing = journal.get("response_processing")
        if (
            not isinstance(processing, dict)
            or set(processing) != _PROCESSING_KEYS
            or journal.get("response_processing_digest") != _digest(processing)
            or processing.get("schema_version")
            != "irene-pass1-response-processing.v1"
            or processing.get("journal_processor_version") != PROCESSOR_VERSION
            or processing.get("executed_processor_version") != PROCESSOR_VERSION
            or processing.get("raw_response_digest")
            != journal.get("raw_response_digest")
            or processing.get("action")
            not in {"strict-json", "drop-one-surplus-final-rbrace"}
            or processing.get("framing") not in {"plain", "json-code-fence"}
            or not _is_digest(processing.get("processed_candidate_digest"))
            or processing.get("parse_status") != "decoded"
            or processing.get("digest_recipe") != "canonical-json-sha256.v1"
        ):
            raise Pass1CallJournalError("Irene response-processing receipt is invalid")
        action = processing["action"]
        if action == "strict-json" and (
            processing.get("removed_byte") is not None
            or processing.get("removed_offset") is not None
            or processing.get("removed_offset_basis") is not None
        ):
            raise Pass1CallJournalError("Irene response-processing action is invalid")
        if action == "drop-one-surplus-final-rbrace" and (
            processing.get("removed_byte") != "}"
            or type(processing.get("removed_offset")) is not int
            or processing["removed_offset"] < 0
            or processing.get("removed_offset_basis")
            != "raw-response-utf8-byte.v1"
        ):
            raise Pass1CallJournalError("Irene response-processing action is invalid")
        expected_processing = _expected_processing_from_raw(journal["raw_response"])
        if any(
            processing.get(key) != value
            for key, value in expected_processing.items()
        ):
            raise Pass1CallJournalError("Irene response-processing binding is invalid")
    if state == "completed":
        result_identity = journal.get("result_identity")
        result = journal.get("result")
        if (
            not isinstance(result_identity, dict)
            or journal.get("result_identity_digest") != _digest(result_identity)
            or not isinstance(result, dict)
            or journal.get("result_digest") != _digest(result)
        ):
            raise Pass1CallJournalError("Irene completed-result identity is invalid")
        if (
            "evidence_normalization_error" in provider_evidence
            or "unsupported_content_shape" in provider_evidence
            or set(result_identity) != _RESULT_IDENTITY_KEYS
            or any(not _is_digest(result_identity[key]) for key in _RESULT_IDENTITY_KEYS)
            or set(result) != {"cache_state"}
        ):
            raise Pass1CallJournalError(
                "Irene completed-result identity semantics are invalid"
            )
        cache_state = result.get("cache_state")
        if (
            not isinstance(cache_state, dict)
            or set(cache_state) != {"cache_prefix", "entries_count"}
            or not isinstance(cache_state.get("cache_prefix"), str)
            or type(cache_state.get("entries_count")) is not int
            or cache_state["entries_count"] < 1
        ):
            raise Pass1CallJournalError("Irene completed-cache semantics are invalid")
        try:
            prefix_value = json.loads(
                cache_state["cache_prefix"], object_pairs_hook=_unique_object
            )
        except (json.JSONDecodeError, Pass1CallJournalError) as exc:
            raise Pass1CallJournalError("Irene completed-cache prefix is invalid") from exc
        if (
            not isinstance(prefix_value, dict)
            or _canonical_bytes(prefix_value).decode("utf-8")
            != cache_state["cache_prefix"]
        ):
            raise Pass1CallJournalError("Irene completed-cache prefix is noncanonical")
        _validate_completed_output_binding(
            journal=journal,
            journal_path=journal_path,
            output=prefix_value,
            result_identity=result_identity,
            provider_evidence=provider_evidence,
        )


def _validate_completed_output_binding(
    *,
    journal: dict[str, Any],
    journal_path: Path,
    output: dict[str, Any],
    result_identity: dict[str, Any],
    provider_evidence: dict[str, Any],
) -> None:
    required = {
        "specialist_id",
        "model_id",
        "lesson_plan",
        "artifact_path",
        "locked_scope",
        "learning_events",
        "plan_authority_receipt",
        "plan_authority_receipt_path",
        "usage",
    }
    allowed = required | {"planning_context_coverage", "planning_provenance"}
    if not required.issubset(set(output)) or not set(output).issubset(allowed):
        raise Pass1CallJournalError("Irene completed output shape is invalid")
    plan = output.get("lesson_plan")
    receipt = output.get("plan_authority_receipt")
    locked_scope = output.get("locked_scope")
    events = output.get("learning_events")
    plan_units = plan.get("plan_units") if isinstance(plan, dict) else None
    artifact_path = Path(output["artifact_path"]) if isinstance(
        output.get("artifact_path"), str
    ) else None
    receipt_path = Path(output["plan_authority_receipt_path"]) if isinstance(
        output.get("plan_authority_receipt_path"), str
    ) else None
    if (
        output.get("specialist_id") != "irene_pass1"
        or output.get("model_id") != journal.get("model_id")
        or not isinstance(plan, dict)
        or not isinstance(receipt, dict)
        or not isinstance(plan_units, list)
        or not plan_units
        or artifact_path is None
        or artifact_path.resolve()
        != (journal_path.parent / "irene-pass1.md").resolve()
        or receipt_path is None
        or receipt_path.resolve()
        != (journal_path.parent / "irene-pass1.plan-authority.json").resolve()
        or _canonical_bytes(output.get("usage"))
        != _canonical_bytes(provider_evidence.get("usage_metadata"))
        or not isinstance(locked_scope, dict)
        or type(locked_scope.get("locked")) is not bool
        or locked_scope["locked"] is not False
        or _canonical_bytes(locked_scope)
        != _canonical_bytes({"plan_units": plan_units, "locked": False})
        or not isinstance(events, list)
        or len(events) != 2
        or not all(isinstance(event, dict) for event in events)
    ):
        raise Pass1CallJournalError("Irene completed output semantics are invalid")
    try:
        from app.marcus.lesson_plan.pass1_authority import assert_receipt_matches_plan

        assert_receipt_matches_plan(plan, receipt)
    except ValueError as exc:
        raise Pass1CallJournalError("Irene completed authority binding is invalid") from exc
    if (
        plan.get("source_span_catalog_digest") != journal["catalog_digest"]
        or receipt.get("catalog_digest") != journal["catalog_digest"]
        or result_identity["plan_digest"] != receipt.get("plan_digest")
        or result_identity["authority_digest"] != receipt.get("authority_digest")
        or result_identity["output_digest"] != _digest(output)
    ):
        raise Pass1CallJournalError("Irene completed result identity is unbound")
    coverage_present = "planning_context_coverage" in output
    plan_provenance_present = "planning_provenance" in plan
    output_provenance_present = "planning_provenance" in output
    if len({coverage_present, plan_provenance_present, output_provenance_present}) != 1:
        raise Pass1CallJournalError("Irene completed planning projections are split")
    coverage: dict[str, Any] | None = None
    if coverage_present:
        try:
            from app.marcus.lesson_plan.planning_context import (
                PlanningContextCoverageReceipt,
            )

            coverage = PlanningContextCoverageReceipt.model_validate(
                output["planning_context_coverage"]
            ).model_dump(mode="json")
        except Exception as exc:
            raise Pass1CallJournalError(
                "Irene completed planning coverage is invalid"
            ) from exc
        if _canonical_bytes(coverage) != _canonical_bytes(
            output["planning_context_coverage"]
        ):
            raise Pass1CallJournalError("Irene completed planning coverage is invalid")
    if plan_provenance_present:
        plan_provenance = plan["planning_provenance"]
        provenance = output["planning_provenance"]
        expected_provenance_keys = {
            "schema_version",
            "ratification_path",
            "ratification_digest",
            "ratified_los_path",
            "ratified_los_digest",
            "intent_path",
            "intent_digest",
            "coverage_lo_status",
        }
        if (
            not isinstance(plan_provenance, dict)
            or not isinstance(provenance, dict)
            or set(provenance) != expected_provenance_keys
            or _canonical_bytes(provenance) != _canonical_bytes(plan_provenance)
            or provenance.get("schema_version") != "0.1"
            or provenance.get("ratification_path") not in {None, "planning-ratification.json"}
            or provenance.get("ratified_los_path") not in {None, "ratified-los.json"}
            or provenance.get("intent_path") not in {
                None,
                "ratified-collateral-intent.yaml",
            }
            or provenance.get("coverage_lo_status")
            not in {"framing_only", "present", "partial", "absent"}
            or coverage is None
            or (
                provenance.get("coverage_lo_status") != coverage["lo_coverage"]
                and not (
                    provenance.get("coverage_lo_status") == "framing_only"
                    and coverage["lo_coverage"] == "present"
                    and not coverage["supported_objective_ids"]
                    and not coverage["weak_or_missing_objective_ids"]
                )
            )
            or any(
                provenance.get(key) is not None and not _is_digest(provenance[key])
                for key in (
                    "ratification_digest",
                    "ratified_los_digest",
                    "intent_digest",
                )
            )
            or any(
                provenance.get(digest_key) is not None
                and provenance.get(path_key) is None
                for path_key, digest_key in (
                    ("ratification_path", "ratification_digest"),
                    ("ratified_los_path", "ratified_los_digest"),
                    ("intent_path", "intent_digest"),
                )
            )
        ):
            raise Pass1CallJournalError("Irene completed planning provenance is invalid")
    timestamp = events[0].get("timestamp")
    if not isinstance(timestamp, str) or events[1].get("timestamp") != timestamp:
        raise Pass1CallJournalError("Irene completed event timestamp is invalid")
    try:
        parsed_timestamp = datetime.fromisoformat(timestamp)
    except ValueError as exc:
        raise Pass1CallJournalError("Irene completed event timestamp is invalid") from exc
    if (
        parsed_timestamp.tzinfo is None
        or parsed_timestamp.utcoffset() is None
        or parsed_timestamp.utcoffset().total_seconds() != 0
        or parsed_timestamp.isoformat() != timestamp
    ):
        raise Pass1CallJournalError("Irene completed event timestamp is invalid")
    base = {"run_id": journal["run_id"], "gate": "G1A", "timestamp": timestamp}
    expected_events = [
        {
            **base,
            "event_type": "scope_decision.set",
            "payload": locked_scope,
        },
        {
            **base,
            "event_type": "plan.locked",
            "payload": {"locked_scope": locked_scope},
        },
    ]
    if _canonical_bytes(events) != _canonical_bytes(expected_events):
        raise Pass1CallJournalError("Irene completed learning events are invalid")


def begin_or_resume_pass1_call(*, run_dir: Path, identity: dict[str, Any]) -> Pass1CallResume:
    """Commit pre-dispatch identity or recover only a durable returned response."""
    _validate_identity(identity)
    _require_current_processor(identity)
    run_dir.mkdir(parents=True, exist_ok=True)
    if run_dir.is_symlink() or not run_dir.is_dir():
        raise Pass1CallJournalError("Irene call journal run directory is unsafe")
    node_id = identity["node_id"]
    path = run_dir / f"irene-pass1-call-{node_id}.v1.json"
    if not path.exists() and not path.is_symlink():
        _atomic_json(path, {**identity, "state": "call_in_progress"})
        return Pass1CallResume(path=path, state="new")
    journal = _load(path)
    _assert_same_identity(journal, identity)
    validate_pass1_call_journal(journal, journal_path=path)
    state = journal.get("state")
    if state == "call_in_progress":
        raise Pass1CallAmbiguousError(
            "Irene provider-call outcome is ambiguous; automatic recall is forbidden"
        )
    raw_response = journal["raw_response"]
    provider_evidence = journal["provider_evidence"]
    return Pass1CallResume(
        path=path,
        state=state,
        raw_response=raw_response,
        provider_evidence=provider_evidence,
        result=journal.get("result") if state == "completed" else None,
        result_identity=journal.get("result_identity") if state == "completed" else None,
        response_processing=journal.get("response_processing"),
    )


def record_pass1_response(
    *,
    path: Path,
    identity: dict[str, Any],
    raw_response: str,
    provider_evidence: dict[str, Any],
) -> None:
    """Durably record exact returned bytes and metadata before candidate parsing."""
    _validate_identity(identity)
    _require_current_processor(identity)
    current = _load(path)
    _assert_same_identity(current, identity)
    validate_pass1_call_journal(current, journal_path=path)
    if current.get("state") != "call_in_progress":
        raise Pass1CallJournalError("Irene call journal is not awaiting a response")
    if "dispatch_exception" in current:
        raise Pass1CallAmbiguousError(
            "Irene provider-call outcome is already ambiguous; response overwrite is forbidden"
        )
    safe_evidence = _canonical_provider_evidence(provider_evidence)
    _atomic_json(
        path,
        {
            **identity,
            "state": "response_received",
            "raw_response": raw_response,
            "raw_response_digest": _digest(raw_response),
            "provider_evidence": safe_evidence,
            "provider_evidence_digest": _digest(safe_evidence),
        },
    )


def record_pass1_dispatch_exception(
    *, path: Path, identity: dict[str, Any], exc: Exception
) -> None:
    """Retain a thrown dispatch outcome while keeping the attempt ambiguous."""
    _validate_identity(identity)
    _require_current_processor(identity)
    current = _load(path)
    _assert_same_identity(current, identity)
    validate_pass1_call_journal(current, journal_path=path)
    if current.get("state") != "call_in_progress":
        raise Pass1CallJournalError("Irene call journal is not in dispatch")
    if "dispatch_exception" in current:
        raise Pass1CallAmbiguousError(
            "Irene provider-call outcome is already ambiguous; exception overwrite is forbidden"
        )
    evidence = {
        "type": type(exc).__name__,
        "message": _scrub_secrets(str(exc)) or "(no message)",
    }
    _atomic_json(
        path,
        {
            **current,
            "dispatch_exception": evidence,
            "dispatch_exception_digest": _digest(evidence),
        },
    )


def record_pass1_candidate_processing(
    *,
    path: Path,
    identity: dict[str, Any],
    action: str,
    framing: str,
    removed_byte: str | None,
    removed_offset: int | None,
    processed_candidate: dict[str, Any],
) -> dict[str, Any]:
    """Bind deterministic candidate decoding before any semantic gate runs."""
    _validate_identity(identity)
    _require_current_processor(identity)
    current = _load(path)
    _assert_same_identity(current, identity)
    validate_pass1_call_journal(current, journal_path=path)
    if current.get("state") not in {
        "response_received",
        "candidate_decoded",
        "completed",
    }:
        raise Pass1CallJournalError("Irene call journal has no processable response")
    receipt = {
        "schema_version": "irene-pass1-response-processing.v1",
        "journal_processor_version": PROCESSOR_VERSION,
        "executed_processor_version": PROCESSOR_VERSION,
        "raw_response_digest": current["raw_response_digest"],
        "action": action,
        "framing": framing,
        "removed_byte": removed_byte,
        "removed_offset": removed_offset,
        "removed_offset_basis": (
            "raw-response-utf8-byte.v1" if removed_offset is not None else None
        ),
        "processed_candidate_digest": _digest(processed_candidate),
        "parse_status": "decoded",
        "digest_recipe": "canonical-json-sha256.v1",
    }
    if current.get("state") in {"candidate_decoded", "completed"}:
        if (
            current.get("response_processing") != receipt
            or current.get("response_processing_digest") != _digest(receipt)
        ):
            raise Pass1CallJournalError(
                "Irene response-processing receipt cannot be replaced"
            )
        return receipt
    updated = {
        **current,
        "state": "candidate_decoded",
        "response_processing": receipt,
        "response_processing_digest": _digest(receipt),
    }
    validate_pass1_call_journal(updated, journal_path=path)
    _atomic_json(path, updated)
    return receipt


def complete_pass1_call(
    *,
    path: Path,
    identity: dict[str, Any],
    result_identity: dict[str, Any],
    result: dict[str, Any],
) -> None:
    """Mark deterministic processing complete without discarding provider evidence."""
    _validate_identity(identity)
    _require_current_processor(identity)
    current = _load(path)
    _assert_same_identity(current, identity)
    validate_pass1_call_journal(current, journal_path=path)
    allowed_states = {"candidate_decoded", "completed"}
    if current.get("state") not in allowed_states:
        raise Pass1CallJournalError("Irene call journal has no returned response")
    safe_result = json.loads(_canonical_bytes(_json_safe(result_identity)))
    safe_output = json.loads(_canonical_bytes(_json_safe(result)))
    completed = {
        **current,
        "state": "completed",
        "result_identity": safe_result,
        "result_identity_digest": _digest(safe_result),
        "result": safe_output,
        "result_digest": _digest(safe_output),
    }
    validate_pass1_call_journal(completed, journal_path=path)
    if current.get("state") == "completed":
        if current != completed:
            raise Pass1CallJournalError(
                "Irene completed-call result cannot be replaced with different bytes"
            )
        return
    _atomic_json(path, completed)


__all__ = [
    "LEGACY_PROCESSOR_VERSION",
    "PROCESSOR_VERSION",
    "SUPPORTED_PROCESSOR_VERSIONS",
    "SCHEMA_VERSION",
    "Pass1CallAmbiguousError",
    "Pass1CallJournalError",
    "Pass1CallResume",
    "begin_or_resume_pass1_call",
    "build_pass1_call_identity",
    "complete_pass1_call",
    "record_pass1_response",
    "record_pass1_candidate_processing",
    "record_pass1_dispatch_exception",
    "response_provider_evidence",
    "validate_pass1_call_journal",
    "validate_provider_evidence",
]
