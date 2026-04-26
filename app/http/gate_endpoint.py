"""HTTP bridge stub for gate verdict resume."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Header, HTTPException
from pydantic import ValidationError

from app.gates import GateError
from app.gates.resume_api import build_transport_response, resume_from_verdict
from app.gates.verdict import OperatorVerdict


def gate_verdict_endpoint(payload: dict[str, Any], *, operator_id: str) -> dict[str, Any]:
    verdict = OperatorVerdict.model_validate({**payload, "operator_id": operator_id})
    command = resume_from_verdict(verdict)
    response = build_transport_response(
        command=command,
        verdict=verdict,
        transport_kind="http",
    )
    response["headers"] = {"X-Gate-Transport": "stub"}
    return response


def create_gate_app() -> FastAPI:
    app = FastAPI(title="gate verdict endpoint", version="0.1.0-slab3")

    @app.post("/gate/verdict")
    def post_gate_verdict(
        payload: dict[str, Any],
        x_operator_id: str | None = Header(default=None),
    ) -> dict[str, Any]:
        if not x_operator_id:
            raise HTTPException(status_code=400, detail="missing X-Operator-Id header")
        try:
            return gate_verdict_endpoint(payload, operator_id=x_operator_id)
        except ValidationError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except GateError as exc:
            if exc.code == "digest_mismatch":
                raise HTTPException(status_code=409, detail=exc.message) from exc
            raise HTTPException(status_code=400, detail=exc.message) from exc

    return app


__all__ = ["create_gate_app", "gate_verdict_endpoint"]
