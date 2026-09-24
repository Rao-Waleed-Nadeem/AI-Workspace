import logging

from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import OperationalError, SQLAlchemyError

from app.core.errors import AppError, RateLimitError


logger = logging.getLogger(__name__)


def _error_response(
    code: str,
    message: str,
    status_code: int,
    details=None,
    headers=None,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "details": details or [],
            }
        },
        headers=headers,
    )


async def app_error_handler(
    request: Request,
    exc: AppError,
) -> JSONResponse:
    """
    Handle application-specific errors.
    """

    if isinstance(exc, RateLimitError):
        logger.warning(
            "Rate limit exceeded for %s %s",
            request.method,
            request.url.path,
        )

        return _error_response(
            code=exc.code,
            message=exc.message,
            status_code=exc.status_code,
            headers={
                "Retry-After": str(exc.retry_after),
            },
        )

    logger.warning(
        "Application error on %s %s: %s",
        request.method,
        request.url.path,
        exc.message,
    )

    return _error_response(
        code=exc.code,
        message=exc.message,
        status_code=exc.status_code,
    )


async def http_error_handler(
    request: Request,
    exc: HTTPException,
) -> JSONResponse:
    """
    Convert FastAPI HTTP exceptions into the
    project's standard error response format.
    """

    status_code = exc.status_code

    status_code_map = {
        400: "bad_request",
        401: "unauthorized",
        403: "forbidden",
        404: "not_found",
        409: "conflict",
        413: "payload_too_large",
        415: "unsupported_media_type",
        422: "unprocessable_entity",
        429: "rate_limited",
    }

    code = status_code_map.get(
        status_code,
        "request_error",
    )

    logger.warning(
        "HTTP error on %s %s: %s",
        request.method,
        request.url.path,
        status_code,
    )

    return _error_response(
        code=code,
        message=str(exc.detail),
        status_code=status_code,
        headers=exc.headers,
    )


async def validation_error_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """
    Handle Pydantic/FastAPI request validation errors.
    """

    details = []

    for error in exc.errors():
        location = error.get("loc", [])

        details.append(
            {
                "field": ".".join(
                    str(item)
                    for item in location
                    if item != "body"
                ),
                "message": error.get(
                    "msg",
                    "Invalid value.",
                ),
                "type": error.get(
                    "type",
                    "validation_error",
                ),
            }
        )

    logger.warning(
        "Validation error on %s %s",
        request.method,
        request.url.path,
    )

    return _error_response(
        code="unprocessable_entity",
        message="Request validation failed.",
        status_code=422,
        details=details,
    )


async def database_error_handler(
    request: Request,
    exc: SQLAlchemyError,
) -> JSONResponse:
    """
    Handle database errors without exposing
    database internals to the client.
    """

    if isinstance(exc, OperationalError):
        code = "database_unavailable"
        message = (
            "The database is temporarily unavailable."
        )
        status_code = 503
    else:
        code = "database_error"
        message = "A database error occurred."
        status_code = 500

    logger.exception(
        "Database error on %s %s",
        request.method,
        request.url.path,
    )

    return _error_response(
        code=code,
        message=message,
        status_code=status_code,
    )


async def unhandled_error_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """
    Final safety net for unexpected exceptions.

    Internal exception details are logged server-side
    but never exposed to the client.
    """

    logger.exception(
        "Unhandled exception on %s %s",
        request.method,
        request.url.path,
    )

    return _error_response(
        code="internal_error",
        message="An unexpected error occurred.",
        status_code=500,
    )