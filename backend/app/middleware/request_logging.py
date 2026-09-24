import logging
from time import perf_counter

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


logger = logging.getLogger("app.request")


class RequestLoggingMiddleware(BaseHTTPMiddleware):

    async def dispatch(
        self,
        request: Request,
        call_next,
    ):
        started = perf_counter()

        try:
            response = await call_next(request)

        except Exception:
            elapsed_ms = (
                perf_counter() - started
            ) * 1000

            logger.exception(
                "%s %s failed after %.0fms",
                request.method,
                request.url.path,
                elapsed_ms,
            )

            raise

        elapsed_ms = (
            perf_counter() - started
        ) * 1000

        message = (
            "%s %s -> %s (%.0fms)"
        )

        if response.status_code >= 500:
            logger.error(
                message,
                request.method,
                request.url.path,
                response.status_code,
                elapsed_ms,
            )

        elif response.status_code >= 400:
            logger.warning(
                message,
                request.method,
                request.url.path,
                response.status_code,
                elapsed_ms,
            )

        else:
            logger.info(
                message,
                request.method,
                request.url.path,
                response.status_code,
                elapsed_ms,
            )

        return response