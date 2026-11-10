"""A single error format for the whole API: Problem Details, RFC 9457. Maps domain errors to status codes."""

from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.shared.domain.errors import Conflict, InvalidData, NotFound


class FieldError(BaseModel):
    field: str
    message: str


class Problem(BaseModel):
    """Problem Details, RFC 9457: the only error format of the API."""

    type: str
    title: str
    status: int
    detail: str | None = None
    errors: list[FieldError] | None = None


TITLES = {
    400: "Invalid request",
    404: "Resource not found",
    405: "Method not allowed",
    409: "Conflict with current state",
    422: "Invalid data",
}


def problem_response(status: int, detail: str | None = None, errors: list[FieldError] | None = None) -> JSONResponse:
    body = Problem(
        type=f"https://clinic.example/problems/{status}",
        title=TITLES.get(status, "Error"),
        status=status,
        detail=detail,
        errors=errors,
    )
    return JSONResponse(
        status_code=status,
        content=body.model_dump(exclude_none=True),
        media_type="application/problem+json",
    )


def responses(*codes: int) -> dict[int | str, dict[str, Any]]:
    """To document a route's errors: `responses=responses(404, 409)`.
    This way /docs and /openapi.json say the same thing as the written contract."""
    return {
        code: {"model": Problem, "description": TITLES[code], "content": {"application/problem+json": {}}}
        for code in codes
    }


def allowed_methods(app: FastAPI, request: Request) -> str:
    """For a 405: every method this path accepts, not only the one of the first route
    encountered. The Allow header is part of the contract (RFC 9110, section 10.2.1).
    Relies on the original_router attribute of FastAPI 0.162: revisit if FastAPI changes."""
    from starlette.routing import Match

    methods: set[str] = set()
    for route in app.routes:
        for sub_route in getattr(getattr(route, "original_router", None), "routes", None) or [route]:
            matched, _ = sub_route.matches(request.scope)
            if matched is not Match.NONE and getattr(sub_route, "methods", None):
                methods |= set(sub_route.methods)
    return ", ".join(sorted(methods - {"HEAD"}))


def install(app: FastAPI) -> None:
    """Register the handlers: domain errors, framework errors and validation errors all become Problems."""

    @app.exception_handler(NotFound)
    async def not_found_to_problem(_: Request, exc: NotFound) -> JSONResponse:
        return problem_response(404, exc.what)

    @app.exception_handler(Conflict)
    async def conflict_to_problem(_: Request, exc: Conflict) -> JSONResponse:
        return problem_response(409, exc.why)

    @app.exception_handler(InvalidData)
    async def invalid_data_to_problem(_: Request, exc: InvalidData) -> JSONResponse:
        # A business rule broken by one field: 422 with errors[], like a Pydantic validation error.
        return problem_response(422, exc.message, [FieldError(field=exc.field, message=exc.message)])

    @app.exception_handler(StarletteHTTPException)  # the base class: also covers the router's 404/405
    async def http_to_problem(request: Request, exc: HTTPException) -> JSONResponse:
        response = problem_response(exc.status_code, str(exc.detail))
        for name, value in (exc.headers or {}).items():
            response.headers[name] = value
        if exc.status_code == 405:
            response.headers["Allow"] = allowed_methods(app, request) or response.headers.get("Allow", "")
        return response

    @app.exception_handler(RequestValidationError)
    async def validation_to_problem(_: Request, exc: RequestValidationError) -> JSONResponse:
        # A body that is not valid JSON is a malformed request, not invalid data.
        if any(e["type"] == "json_invalid" for e in exc.errors()):
            return problem_response(400, "Request body is not valid JSON")
        errors = []
        for e in exc.errors():
            field = ".".join(str(p) for p in e["loc"] if p not in ("body", "query", "path"))
            errors.append(FieldError(field=field or "body", message=e["msg"]))
        return problem_response(422, f"{len(errors)} invalid field(s)", errors)
